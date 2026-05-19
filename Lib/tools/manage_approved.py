"""
Manage session-approved commands - 修复版
"""
import os
import sys
import json

from Lib.base.base import tool

# 修复：定义全局变量
approved_commands = set()

@tool(
    name="manage_approved",
    description="Manage session-approved commands",
    schema={
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["list", "clear"]
            }
        },
        "required": ["action"]
    }
)
def manage_approved(action: str) -> str:
    global approved_commands
    try:
        if action == "list":
            if not approved_commands:
                return "No approved commands for this session."
            return "\n".join(f"  - {c}" for c in sorted(approved_commands))
        elif action == "clear":
            count = len(approved_commands)
            approved_commands.clear()
            return f"Cleared {count} approved commands"
        else:
            return f"Unknown action: {action}"
    except Exception as e:
        return f"Error: {e}"
