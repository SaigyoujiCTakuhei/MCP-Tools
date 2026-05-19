"""
List contents of a directory
"""
import os
import sys
import json

from Lib.base.base import tool

@tool(
    name="list_directory",
    description="List contents of a directory",
    schema={
    "type": "object",
    "properties": {
        "path": {
            "type": "string",
            "default": "."
        }
    },
    "required": []
}
)
def list_directory(path: str = ".") -> str:
    try:
        items = [f"{item}/" if os.path.isdir(os.path.join(path, item)) else item for item in sorted(os.listdir(path))]
        return "\n".join(items) if items else "(empty)"
    except Exception as e: return f"Error: {e}"