"""
Manage the command blacklist - 修复版
"""
import os
import sys
import json

from Lib.base.base import tool

# 修复：定义全局变量，否则 global 语句会报错
blacklisted_commands = set()

@tool(
    name="manage_blacklist",
    description="Manage the command blacklist",
    schema={
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["list", "add", "remove", "clear"]
            },
            "command": {
                "type": "string"
            }
        },
        "required": ["action"]
    }
)
def manage_blacklist(action: str, command: str = "") -> str:
    global blacklisted_commands
    try:
        if action == "list":
            if not blacklisted_commands:
                return "Blacklist is empty."
            return "\n".join(f"  - {c}" for c in sorted(blacklisted_commands))
        elif action == "add":
            if not command:
                return "Error: Command required for 'add' action"
            blacklisted_commands.add(command)
            return f"Added '{command}' to blacklist"
        elif action == "remove":
            if not command:
                return "Error: Command required for 'remove' action"
            if command in blacklisted_commands:
                blacklisted_commands.discard(command)
                return f"Removed '{command}' from blacklist"
            return f"Command '{command}' not in blacklist"
        elif action == "clear":
            count = len(blacklisted_commands)
            blacklisted_commands.clear()
            return f"Cleared {count} commands from blacklist"
        else:
            return f"Unknown action: {action}"
    except Exception as e:
        return f"Error: {e}"
