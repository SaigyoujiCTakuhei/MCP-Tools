"""
Create a directory
"""
import os
import sys
import json

from Lib.base.base import tool

@tool(
    name="create_directory",
    description="Create a directory",
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
def create_directory(path: str) -> str:
    try:
        os.makedirs(path, exist_ok=True)
        return f"Created: '{path}'"
    except Exception as e: return f"Error: {e}"