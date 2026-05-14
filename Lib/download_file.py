"""
Download a file from a URL
"""
import os
import sys
import json

from Lib.base import tool

@tool(
    name="download_file",
    description="Download a file from a URL",
    schema={
    "type": "object",
    "properties": {
        "url": {
            "type": "string"
        },
        "filename": {
            "type": "string"
        }
    },
    "required": [
        "url",
        "filename"
    ]
}
)
def download_file(url: str, filename: str) -> str:
    try:
        import httpx
        with httpx.get(url, timeout=30, follow_redirects=True) as r:
            r.raise_for_status()
            # 【猫娘修复】Issue 3: 修复目录创建逻辑缺陷，避免空路径或根路径导致 os.makedirs 误操作
            dir_path = os.path.dirname(filename)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            with open(filename, 'wb') as f:
                f.write(r.content)
        return f"Downloaded to '{filename}' ({len(r.content)} bytes)"
    except Exception as e:
        return f"Error: {e}"