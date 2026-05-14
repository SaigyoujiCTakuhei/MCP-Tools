"""
Get Everything info
"""
import os
import sys
import json

from Lib.base import tool

@tool(
    name="get_everything_info",
    description="Get Everything info",
    schema={
    "type": "object",
    "properties": {},
    "required": []
}
)
def get_everything_info() -> dict:
    return {"name": "Everything", "version": "1.5.0", "status": "running"}