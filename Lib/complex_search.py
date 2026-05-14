"""
Complex combined search - 修复版
"""
import os
import sys
import json

from Lib.base import tool

@tool(
    name="complex_search",
    description="Complex combined search",
    schema={
        "type": "object",
        "properties": {
            "keywords": {
                "type": "array",
                "default": None
            },
            "filters": {
                "type": "array",
                "default": None
            },
            "match_case": {
                "type": "boolean",
                "default": False
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
                "default": None
            }
        },
        "required": []
    }
)
def complex_search(keywords=None, filters=None, match_case=False, match_path=False, match_whole_word=False, regex=False, sort_type=1, max_results=10, return_properties=None) -> str:
    try:
        from everytools import Search, SearchBuilder, SortType
        builder = SearchBuilder()
        if keywords:
            builder.set_query(" ".join(keywords))
        if match_case:
            builder.set_match_case()
        if match_path:
            builder.set_match_path()
        if match_whole_word:
            builder.set_match_whole_word()
        if regex:
            builder.set_regex()
        if sort_type != 1:
            builder.set_sort_type(SortType(sort_type))
        
        # 【猫娘修复】Issue 8: 增强 filters 处理健壮性，防止 everytools 版本差异导致 AttributeError
        if filters:
            for f in filters:
                t, p = f.get("type"), f.get("params", {})
                try:
                    if t == "file_filter":
                        if "with_extensions" in p:
                            builder.filter.with_extensions(*p["with_extensions"])
                    elif t == "date_filter":
                        builder.filter.by_date(p.get("by_date"), p.get("in_range"))
                except AttributeError:
                    pass  # 忽略不支持的过滤器类型
            
        results = builder.build().execute()[:max_results]
        
        cols = ["name", "path", "size", "date_modified"] if return_properties is None else return_properties
        
        # 转换为字典列表
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