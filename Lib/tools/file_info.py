"""
Get file metadata
"""
import os
import sys
import json

from Lib.base.base import tool

@tool(
    name="file_info",
    description="Get file metadata",
    schema={
    "type": "object",
    "properties": {
        "file_path": {
            "type": "string"
        }
    },
    "required": [
        "file_path"
    ]
}
)
def file_info(file_path: str) -> dict:
    try:
        s = os.stat(file_path)
        return {"success": True, "size": s.st_size, "modified": s.st_mtime, "accessed": s.st_atime, "created": s.st_ctime, "permissions": oct(s.st_mode)}
    except Exception as e: return {"success": False, "error": str(e)}