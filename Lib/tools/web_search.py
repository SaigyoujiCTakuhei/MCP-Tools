"""
Search the web for information
"""
import os
import sys
import json

from Lib.base.base import tool

@tool(
    name="web_search",
    description="Search the web for information",
    schema={
    "type": "object",
    "properties": {
        "query": {
            "type": "string"
        },
        "num_results": {
            "type": "integer",
            "default": 5
        }
    },
    "required": [
        "query"
    ]
}
)
def web_search(query: str, num_results: int = 5) -> str:
    try:
        from ddgs import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=num_results):
                results.append(f"Title: {r['title']}\nURL: {r['href']}\n{r['body']}")
        return "\n---\n".join(results) if results else "No results"
    except ImportError: return "Error: ddgs not installed"
    except Exception as e: return f"Error: {e}"