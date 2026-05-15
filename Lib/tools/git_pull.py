"""
Pull latest changes from a git repository
"""
import os
import sys
import json

from Lib.base.base import tool

@tool(
    name="git_pull",
    description="Pull latest changes from a git repository",
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
def git_pull(path: str) -> str:
    import subprocess
    try:
        result = subprocess.run(["git", "pull", "origin", "HEAD"], capture_output=True, text=True, cwd=path)
        return result.stdout or result.stderr or f"Exit: {result.returncode}"
    except Exception as e: return f"Error: {e}"