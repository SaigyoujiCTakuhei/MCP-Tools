"""
Fetch and extract text content from a web page
"""
import os
import sys
import json

from Lib.base.base import tool

@tool(
    name="web_fetch",
    description="Fetch and extract text content from a web page",
    schema={
    "type": "object",
    "properties": {
        "url": {
            "type": "string"
        },
        "max_length": {
            "type": "integer",
            "default": 10000
        }
    },
    "required": [
        "url"
    ]
}
)
def web_fetch(url: str, max_length: int = 10000) -> str:
    try:
        import httpx
        from selectolax.parser import HTMLParser
        resp = httpx.get(url, timeout=10, follow_redirects=True)
        resp.raise_for_status()
        tree = HTMLParser(resp.text)
        for tag in tree.css("script, style, nav, footer, header"): tag.decompose()
        text = tree.text()
        if len(text) > max_length: text = text[:max_length] + f"\n... [truncated]"
        return text.strip()
    except ImportError: return "Error: httpx/selectolax not installed"
    except Exception as e: return f"Error: {e}"