"""
Download a file from a URL
"""
import os
import sys
import json

from Lib.base.base import tool

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
        # 【猫娘修改】：移除对 httpx.get() 直接调用的 with 上下文管理语法，显式获取 Response 对象并手动管理生命周期，彻底规避 'Response object does not support the context manager protocol' 兼容异常。
        # 【修改时间】：2026-05-15 13:18:30。
        response = httpx.get(url, timeout=30, follow_redirects=True)
        response.raise_for_status()
        
        dir_path = os.path.dirname(filename)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        with open(filename, 'wb') as f:
            f.write(response.content)
            
        return f"Downloaded to '{filename}' ({len(response.content)} bytes)"
    except Exception as e:
        return f"Error: {e}"
