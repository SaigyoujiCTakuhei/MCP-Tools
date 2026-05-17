"""
Execute a shell command
"""
import os
import sys
import json

from Lib.base.base import tool

@tool(
    name="run_command",
    description="Execute a shell command",
    schema={
    "type": "object",
    "properties": {
        "command": {
            "type": "string"
        },
        "timeout": {
            "type": "integer",
            "default": 30
        }
    },
    "required": [
        "command"
    ]
}
)
def run_command(command: str, timeout: int = 30) -> str:
    import subprocess
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        out = []
        if result.stdout: out.append(f"STDOUT:\n{result.stdout}")
        if result.stderr: out.append(f"STDERR:\n{result.stderr}")
        out.append(f"Exit code: {result.returncode}")
        return "\n".join(out)
    except subprocess.TimeoutExpired: return f"Timed out after {timeout}s"
    except Exception as e: return f"Error: {e}"