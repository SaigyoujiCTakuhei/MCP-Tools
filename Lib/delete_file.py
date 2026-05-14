"""
Delete a file
"""
import os
import sys
import json

from Lib.base import tool

@tool(
    name="delete_file",
    description="Delete a file",
    schema={
    "type": "object",
    "properties": {
        "path": {
            "type": "string"
        }
    },
    "required": [
        "path"
    ]
}
)
def delete_file(path: str) -> str:
    try:
        if os.path.isdir(path): return f"'{path}' is a directory"
        os.unlink(path)
        return f"Deleted: '{path}'"
    except Exception as e: return f"Error: {e}"