"""
Read contents of a file from the filesystem
"""
import os
import sys
import json

from Lib.base import tool

@tool(
    name="read_file",
    description="Read contents of a file from the filesystem",
    schema={
    "type": "object",
    "properties": {
        "path": {
            "type": "string",
            "description": "File path"
        }
    },
    "required": [
        "path"
    ]
}
)
def read_file(path: str) -> str:
    try:
        with open(path, 'r', encoding='utf-8') as f: return f.read()
    except Exception as e: return f"Error: {e}"