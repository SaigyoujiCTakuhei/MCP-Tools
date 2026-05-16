"""
Search for text patterns in files
"""
import os
import sys
import json

from Lib.base.base import tool

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
    import re
    try:
        regex = re.compile(pattern)
        matches = []
        for root, _, files in os.walk(path):
            for f in files:
                if file_pattern == "*" or f.endswith(file_pattern):
                    for i, line in enumerate(open(os.path.join(root, f), 'r', encoding='utf-8', errors='ignore'), 1):
                        if regex.search(line): matches.append(f"{os.path.join(root, f)}:{i}: {line.rstrip()}")
        return "\n".join(matches[:100]) if matches else f"No matches for '{pattern}'"
    except re.error as e: return f"Invalid regex: {e}"
    except Exception as e: return f"Error: {e}"