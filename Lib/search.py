"""
Search files with Everything - 修复版
"""
import os
import sys
import json

from Lib.base import tool

@tool(
    name="search",
    description="Search files with Everything",
    schema={
        "type": "object",
        "properties": {
            "query_string": {
                "type": "string",
                "description": "Search query"
            },
            "match_case": {
                "type": "boolean",
                "default": False  # 修复：Python False
            },
            "match_path": {
                "type": "boolean",
                "default": False
            },
            "match_whole_word": {
                "type": "boolean",
                "default": False
            },
            "regex": {
                "type": "boolean",
                "default": False
            },
            "sort_type": {
                "type": "integer",
                "default": 1
            },
            "max_results": {
                "type": "integer",
                "default": 10
            },
            "return_properties": {
                "type": "array",
                "default": None  # 修复：Python None
            }
        },
        "required": [
            "query_string"
        ]
    }
)
def search(query_string: str, match_case: bool = False, match_path: bool = False, match_whole_word: bool = False, regex: bool = False, sort_type: int = 1, max_results: int = 10, return_properties: list[str] = None) -> str:
    try:
        from everytools import Search, SearchBuilder, SortType
        builder = SearchBuilder()
        builder.set_query(query_string)
        if match_case: builder.set_match_case()
        if match_path: builder.set_match_path()
        if match_whole_word: builder.set_match_whole_word()
        if regex: builder.set_regex()
        if sort_type != 1: builder.set_sort_type(SortType(sort_type))
        
        results = builder.build().execute()[:max_results]
        
        cols = ["name", "path", "size", "date_modified"] if return_properties is None else return_properties
        rows = [{c: getattr(r, c, "") for c in cols} for r in results]
        
        # 修复：正确计算列宽
        widths = [max((len(str(row.get(c, ""))) for row in rows), default=len(c)) for c in cols]
        
        def line(cells): 
            return "| " + " | ".join(str(c).ljust(widths[i]) for i, c in enumerate(cells)) + " |"
            
        sep = "+-" + "-+-".join("-"*w for w in widths) + "-+"
        
        lines = [sep, line(cols), sep] + [line([str(row.get(c, "")) for c in cols]) for row in rows] + [sep]
        return "\n".join(lines)
        
    except Exception as e: 
        return f"Error: {e}"
