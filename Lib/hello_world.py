"""
A simple hello world tool
"""
import os
import sys
import json

from Lib.base import tool

@tool(
    name="hello_world",
    description="A simple hello world tool",
    schema={
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "Name to greet"
        }
    },
    "required": [
        "name"
    ]
}
)
def hello_world(name: str) -> str:
    return f"Hello, {name}! Welcome to Ent MCP."