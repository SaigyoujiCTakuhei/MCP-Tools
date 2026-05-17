"""
Execute a Python script
"""
import os
import sys
import json

from Lib.base.base import tool

@tool(
    name="run_python_script",
    description="Execute a Python script",
    schema={
    "type": "object",
    "properties": {
        "script_path": {
            "type": "string"
        },
        "args": {
            "type": "string",
            "default": ""
        }
    },
    "required": [
        "script_path"
    ]
}
)
def run_python_script(script_path: str, args: str = "") -> str:
    import subprocess
    cmd = ["python", script_path] + args.split() if args else ["python", script_path]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        out = []
        if r.stdout: out.append(f"STDOUT:\n{r.stdout}")
        if r.stderr: out.append(f"STDERR:\n{r.stderr}")
        out.append(f"Exit: {r.returncode}")
        return "\n".join(out)
    except subprocess.TimeoutExpired: return "Timed out"
    except Exception as e: return f"Error: {e}"