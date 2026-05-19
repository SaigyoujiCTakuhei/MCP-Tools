"""
Search for text patterns in files
"""
import os
import sys
import json
import re

from Lib.base.base import tool

# 【猫娘修改】：预定义需跳过的缓存/配置目录
SKIP_DIRS = {'__pycache__', 'node_modules', '.git', '.svn', '.hg', '.tox', '.pytest_cache'}

def _is_binary_file(file_path: str) -> bool:
    """【猫娘修改】：安全检测二进制文件。读取前1KB检查\\x00及乱码比例"""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            if b'\x00' in chunk:
                return True
            text_chars = set(range(7, 14)) | set(range(27, 33)) | set(range(33, 127))
            if chunk:
                non_text = sum(1 for b in chunk if b not in text_chars)
                if non_text / len(chunk) > 0.3:
                    return True
    except (IOError, OSError):
        pass
    return False

@tool(
    name="grep",
    description="Search for text patterns in files",
    schema={
    "type": "object",
    "properties": {
        "pattern": {
            "type": "string"
        },
        "path": {
            "type": "string",
            "default": "."
        },
        "file_pattern": {
            "type": "string",
            "default": "*"
        }
    },
    "required": [
        "pattern"
    ]
}
)
def grep(pattern: str, path: str = ".", file_pattern: str = "*") -> str:
    try:
        regex = re.compile(pattern)
    except re.error as e: 
        return f"Invalid regex: {e}"

    matches = []
    for root, dirs, files in os.walk(path):
        # 【猫娘修改】：原地过滤 dirs，阻止进入缓存/隐藏目录
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
        
        for f in files:
            if file_pattern != "*" and not f.endswith(file_pattern):
                continue
                
            file_path = os.path.join(root, f)
            try:
                # 【猫娘修改】：拦截二进制文件，防止崩溃
                if _is_binary_file(file_path):
                    continue
                    
                # 【猫娘修改】：使用上下文管理器，提升编码安全性
                with open(file_path, 'r', encoding='utf-8', errors='surrogateescape') as fh:
                    for i, line in enumerate(fh, 1):
                        if regex.search(line):
                            matches.append(f"{file_path}:{i}: {line.rstrip()}")
                            if len(matches) >= 100:
                                return "\n".join(matches)
            except Exception as e:
                # 【猫娘修改】：单文件异常不阻断全局扫描
                continue
                
    return "\n".join(matches[:100]) if matches else f"No matches for '{pattern}'"
