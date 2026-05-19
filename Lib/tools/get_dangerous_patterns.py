"""
Get list of dangerous command patterns
"""
import os
import sys
import json

from Lib.base.base import tool

@tool(
    name="get_dangerous_patterns",
    description="Get list of dangerous command patterns",
    schema={
    "type": "object",
    "properties": {},
    "required": []
}
)
def get_dangerous_patterns() -> str:
    return "\n".join(f"  - {p}" for p in ["rm -rf /", "dd to disk", "shutdown", "chmod -R 777", "curl | sh", "Fork bomb"])