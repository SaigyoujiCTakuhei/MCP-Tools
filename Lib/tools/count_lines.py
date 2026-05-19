"""
Count lines of code in files by extension
"""
import os
import sys
import json

from Lib.base.base import tool

@tool(
    name="count_lines",
    description="Count lines of code in files by extension",
    schema={
    "type": "object",
    "properties": {
        "path": {
            "type": "string",
            "default": "."
        },
        "extensions": {
            "type": "string"
        }
    },
    "required": [
        "path"
    ]
}
)
def count_lines(path: str = ".", extensions: str = "") -> str:
    exts = [f".{e.strip().lstrip('.')}" for e in extensions.split(",")] if extensions else None
    total, files, details = 0, 0, []
    for root, _, fs in os.walk(path):
        for f in fs:
            fp = os.path.join(root, f)
            if exts is None or any(fp.endswith(e) for e in exts):
                try:
                    lines = len(open(fp, 'r', encoding='utf-8', errors='ignore').readlines())
                    total += lines; files += 1; details.append(f"  {fp}: {lines}")
                except: pass
    return f"Total: {total} lines in {files} files\n" + "\n".join(details[:20]) if details else f"No files in '{path}'"