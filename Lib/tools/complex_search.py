"""
Complex combined search - 原版功能还原版（类型转换修复）
"""
import os
import sys
import json
import re

from Lib.base.base import tool


def _safe_int(val, default=0) -> int:
    """安全转换为整数，兼容 MCP 传输层 string/int 混传"""
    if val is None:
        return default
    if isinstance(val, bool):
        return 1 if val else 0
    if isinstance(val, (int, float)):
        return int(val)
    if isinstance(val, str):
        val = val.strip()
        if not val:
            return default
        try:
            return int(val)
        except ValueError:
            try:
                return int(float(val))
            except ValueError:
                return default
    return default


def _safe_bool(val, default=False) -> bool:
    """安全转换为布尔值，兼容 MCP 传输层 string/bool 混传"""
    if val is None:
        return default
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return bool(val)
    if isinstance(val, str):
        return val.lower() in ("true", "1", "yes", "on")
    return default


def _safe_list(val, default=None) -> list[str]:
    """安全转换为字符串列表，兼容 MCP 传输层 array/str 混传"""
    if val is None:
        return default
    if isinstance(val, (list, tuple)):
        return [str(v).strip() for v in val if v]
    if isinstance(val, str):
        # 兼容逗号/分号/空格/制表符分隔
        parts = re.split(r'[,\s;]+', val.strip())
        return [p for p in parts if p]
    return default or []


def _escape_regex_pipe(keywords: list[str], enable_regex: bool) -> tuple[list[str], bool]:
    """安全处理正则表达式关键词中的管道符，防止底层拦截"""
    if not enable_regex or not keywords:
        return keywords, False
    escaped_list = []
    modified = False
    for kw in keywords:
        if isinstance(kw, str) and '|' in kw:
            escaped = re.sub(r'(?<!\\)\|', r'\|', kw)
            escaped_list.append(escaped)
            if escaped != kw:
                modified = True
        else:
            escaped_list.append(kw)
    return escaped_list, modified


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
def complex_search(
    keywords=None,
    filters=None,
    match_case=False,
    match_path=False,
    match_whole_word=False,
    regex=False,
    sort_type=1,
    max_results=10,
    return_properties=None
) -> str:
    """使用 Everything 进行复杂组合搜索。

    Args:
        keywords: 搜索关键词列表，支持数组或逗号分隔字符串。
        filters: 过滤器列表，每个过滤器是一个 dict，包含 type 和 params。
        match_case: 是否区分大小写，默认 False。
        match_path: 是否匹配完整路径，默认 False。
        match_whole_word: 是否全词匹配，默认 False。
        regex: 是否启用正则表达式，默认 False。
        sort_type: 排序类型，默认 1。
        max_results: 最大返回结果数，默认 10。
        return_properties: 返回字段列表，支持数组或逗号分隔字符串。

    Returns:
        ASCII 表格格式的搜索结果字符串。
    """
    try:
        from everytools import Search, SearchBuilder, SortType
        from everytools.query.filters import (
            FileFilter, DateFilter, MediaFilter, DocumentFilter, SizeFilter
        )

        # 【猫娘修改】：恢复原版完整功能，兼容 MCP 传输层类型转换。【修改时间】：2026-05-15 17:40:00。
        return_properties = return_properties or [
            "name", "path", "full_path", "is_file", "is_folder", "is_volume",
            "extension", "size", "date_created", "date_modified", "date_accessed", "date_run"
        ]

        # 【猫娘修复】Issue 1: MCP 传输层将 integer/boolean 转为字符串，增加安全转换函数防底层 TypeError。【修改时间】：2026-05-15 17:40:00。
        sort_type = _safe_int(sort_type, 1)
        max_results = _safe_int(max_results, 10)
        match_case = _safe_bool(match_case, False)
        match_path = _safe_bool(match_path, False)
        match_whole_word = _safe_bool(match_whole_word, False)
        regex = _safe_bool(regex, False)

        # 【猫娘修复】Issue 2: return_properties 未做 split 容错，渲染异常。【修改时间】：2026-05-15 17:40:00。
        cols = _safe_list(return_properties, [
            "name", "path", "full_path", "is_file", "is_folder", "is_volume",
            "extension", "size", "date_created", "date_modified", "date_accessed", "date_run"
        ])

        # 【猫娘修复】Issue 3: keywords 支持 split 容错 + 管道符转义防底层拦截。【修改时间】：2026-05-15 17:40:00。
        raw_keywords = keywords or []
        keywords_list = _safe_list(raw_keywords, [])
        if regex and keywords_list:
            keywords_list, _ = _escape_regex_pipe(keywords_list, True)

        filters = filters or []

        builder = SearchBuilder()
        if keywords_list:
            builder.keywords(*keywords_list)
        
        builder.match_case(match_case)
        builder.match_path(match_path)
        builder.match_whole_word(match_whole_word)
        builder.use_regex(regex)

        builder.sort_by(SortType(sort_type))
        builder.limit(max_results)

        # 【猫娘修改】：防御 filters 参数反序列化异常（MCP 传输可能将 dict 数组转为 JSON 字符串数组）。【修改时间】：2026-05-15 17:40:00。
        parsed_filters = []
        for f in filters:
            if isinstance(f, str):
                try:
                    f = json.loads(f)
                except json.JSONDecodeError:
                    continue
            if isinstance(f, dict):
                parsed_filters.append(f)

        for f in parsed_filters:
            f_type = f.get("type")
            params = f.get("params", {})

            if f_type == "file_filter":
                ff = FileFilter()
                if "with_extensions" in params:
                    ff.with_extensions(*params["with_extensions"])
                if "with_size_range" in params:
                    sr = params["with_size_range"]
                    # 【猫娘修复】Issue 1: size_filter 参数安全转换，防止 str vs int 比较异常。【修改时间】：2026-05-15 17:40:00。
                    min_size = _safe_int(sr.get("min_size"))
                    max_size = _safe_int(sr.get("max_size"))
                    ff.with_size_range(min_size if min_size > 0 else None, max_size if max_size > 0 else None)
                if "with_content" in params:
                    ff.with_content(params["with_content"])
                if params.get("duplicates_only"):
                    ff.duplicates_only()
                builder.filter(ff)

            elif f_type == "date_filter":
                df = DateFilter()
                by_date = params.get("by_date", "modified_date")
                if by_date == "created_date":
                    df.by_created_date()
                elif by_date == "accessed_date":
                    df.by_accessed_date()
                else:
                    df.by_modified_date()
                date_range = params.get("in_range")
                if date_range and len(date_range) == 2:
                    df.in_range(date_range[0], date_range[1])
                builder.filter(df)

            elif f_type == "size_filter":
                sf = SizeFilter()
                # 【猫娘修复】Issue 1: size_filter 核心参数安全转换，防止底层 C 绑定比较 str vs int 抛 TypeError。【修改时间】：2026-05-15 17:40:00。
                min_bytes = _safe_int(params.get("gt"))
                max_bytes = _safe_int(params.get("lt"))
                if min_bytes > 0 and max_bytes > 0:
                    sf.between(min_bytes, max_bytes)
                elif min_bytes > 0:
                    sf.larger_than(min_bytes)
                elif max_bytes > 0:
                    sf.smaller_than(max_bytes)
                builder.filter(sf)

            elif f_type == "media_filter":
                mf = MediaFilter(params.get("file_type", "all"))
                builder.filter(mf)

            elif f_type == "document_filter":
                doc_f = DocumentFilter(params.get("file_type", "all"))
                builder.filter(doc_f)

        search_obj = builder.execute()
        result_set = search_obj.get_results()
        
        # 【猫娘修改】：恢复原版结果处理逻辑，不强制切片，保留完整统计上下文。【修改时间】：2026-05-15 17:40:00。
        results = list(result_set)
        
        dict_rows = []
        for item in results:
            d = vars(item) if hasattr(item, '__dict__') else item
            if isinstance(d, dict):
                dict_rows.append({k: d[k] for k in cols if k in d})
            else:
                dict_rows.append(d)

        # 原版统计信息提取
        total = result_set.total_results
        total_files = result_set.total_files
        total_folders = result_set.total_folders

        # 原版格式化函数
        def _format_ascii_table(title: str, columns: list[str], rows: list[dict]) -> str:
            str_rows = [[str(r.get(c, "")) for c in columns] for r in rows if isinstance(r, dict)]
            col_widths = []
            for i, c in enumerate(columns):
                width = len(c)
                for row in str_rows:
                    width = max(width, len(row[i]))
                col_widths.append(width)

            def _row_line(cells):
                return "| " + " | ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(cells)) + " |"

            separator = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
            lines = [title, separator, _row_line(columns), separator]
            for row in str_rows:
                lines.append(_row_line(row))
            lines.append(separator)
            return "\n".join(lines)

        query_str = builder.build_query_string()
        title = f"复杂搜索结果: {query_str} (返回 {len(dict_rows)} 条, 总计 {total} 条, 文件 {total_files}, 文件夹 {total_folders})"
        return _format_ascii_table(title, cols, dict_rows)

    except Exception as e:
        return f"Error: {e}"
