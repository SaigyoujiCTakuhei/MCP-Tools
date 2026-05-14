"""
Reverse a string
"""
import os
import sys
import json

from Lib.base import tool

@tool(
    name="reverse_text",
    description="Reverse a string",
    schema={
    "type": "object",
    "properties": {
        "text": {
            "type": "string",
            "description": "Text to reverse"
        }
    },
    "required": [
        "text"
    ]
}
)
def reverse_text(text: str) -> str:
    return text[::-1]