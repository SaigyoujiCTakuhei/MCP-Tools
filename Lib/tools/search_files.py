"""
Search for files matching a glob pattern
"""
import os
import sys
import json

from Lib.base.base import tool

@tool(
    name="search_files",
    description="Search for files matching a glob pattern",
    schema={
    "type": "object",
    "properties": {
        "pattern": {
            "type": "string"
        },
        "path": {
            "type": "string",
            "default": "."
        }
    },
    "required": [
        "pattern"
    ]
}
)
def search_files(pattern: str, path: str = ".") -> str:
    try:
        import glob
        matches = glob.glob(os.path.join(path, pattern), recursive=True)
        return "\n".join(matches) if matches else f"No files matching '{pattern}'"
    except Exception as e: return f"Error: {e}"