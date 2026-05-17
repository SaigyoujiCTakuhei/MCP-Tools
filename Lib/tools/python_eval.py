"""
Run a Python code snippet
"""
import os
import sys
import json
import threading
import io
import traceback
import queue

from Lib.base.base import tool

@tool(
    name="python_eval",
    description="Run a Python code snippet",
    schema={
    "type": "object",
    "properties": {
        "code_str": {
            "type": "string"
        },
        "timeout": {
            "type": "integer",
            "default": 30
        }
    },
    "required": [
        "code_str"
    ]
}
)
def python_eval(code_str: str, timeout: int = 30) -> dict:
    # 【猫娘修复】Issue 6: 替换 multiprocessing 为 threading，避免 Windows 下 spawn 协议导致的递归创建进程问题
    result_q = queue.Queue()
    out_buffer, err_buffer = io.StringIO(), io.StringIO()
    original_stdout, original_stderr = sys.stdout, sys.stderr

    def _exec_thread():
        sys.stdout, sys.stderr = out_buffer, err_buffer
        try:
            try:
                result_q.put(('success', {'result': eval(compile(code_str, '', 'eval'), {}), 'stdout': out_buffer.getvalue(), 'stderr': err_buffer.getvalue()}))
            except SyntaxError:
                exec(compile(code_str, '', 'exec'), {})
                result_q.put(('success', {'result': None, 'stdout': out_buffer.getvalue(), 'stderr': err_buffer.getvalue()}))
        except Exception as e:
            result_q.put(('error', {'exception': str(e), 'traceback': traceback.format_exc()}))
        finally:
            sys.stdout, sys.stderr = original_stdout, original_stderr

    thread = threading.Thread(target=_exec_thread)
    thread.daemon = True
    thread.start()
    thread.join(timeout=timeout)

    if thread.is_alive():
        return {"success": False, "error": f"Timed out after {timeout}s"}
    
    return result_q.get_nowait() if not result_q.empty() else {"success": False, "error": "Unknown error"}