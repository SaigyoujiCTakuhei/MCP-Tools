"""
Clone a git repository
"""
import os
import sys
import json

from Lib.base import tool

@tool(
    name="git_clone",
    description="Clone a git repository",
    schema={
    "type": "object",
    "properties": {
        "url": {
            "type": "string"
        },
        "path": {
            "type": "string",
            "default": ""
        }
    },
    "required": [
        "url"
    ]
}
)
def git_clone(url: str, path: str = "") -> str:
    import subprocess
    try:
        subprocess.run(["git", "clone", url, path or ""], check=True, capture_output=True, text=True)
        return f"Cloned to '{path or '.'}'"
    except subprocess.CalledProcessError as e: return f"Error: {e.stderr}"
    except Exception as e: return f"Error: {e}"