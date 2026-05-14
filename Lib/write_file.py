"""
Write content to a file in the filesystem
"""
import os
import sys
import json

from Lib.base import tool

@tool(
    name="write_file",
    description="Write content to a file in the filesystem",
    schema={
    "type": "object",
    "properties": {
        "path": {
            "type": "string"
        },
        "content": {
            "type": "string"
        },
        "mode": {
            "type": "string",
            "default": "write"
        }
    },
    "required": [
        "path",
        "content"
    ]
}
)
# 【猫娘修改】：函数签名中增加 mode 参数，默认为 'write' 以保持向后兼容。
def write_file(path: str, content: str, mode: str = "write") -> str:
    try:
        dir_path = os.path.dirname(path)
        # 【猫娘修复】Issue 3: 修复目录创建逻辑缺陷，避免空路径或根路径导致 os.makedirs 误操作
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        # 【猫娘修改】：根据 mode 参数动态选择文件打开模式，'w' 为覆盖，'a' 为追加。
        file_mode = 'w' if mode.lower() == 'write' else 'a'
        
        with open(path, file_mode, encoding='utf-8') as f:
            f.write(content)
            
        # 【猫娘修改】：返回消息增加操作类型区分。
        action = "appended content to" if file_mode == 'a' else "wrote to"
        return f"Successfully {action} '{path}'"
    except Exception as e:
        return f"Error: {e}"