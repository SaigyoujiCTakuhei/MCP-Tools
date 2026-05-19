"""
Search files with Everything - 原版功能还原版（类型转换修复）
"""
import os
import sys
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


def _escape_regex_pipe(pattern: str) -> tuple[str, bool]:
    """安全处理正则表达式中的管道符，防止底层拦截"""
    if not pattern or '|' not in pattern:
        return pattern, False
    # 将裸管道符转义为 \|，避免被底层解析为逻辑或
    escaped = re.sub(r'(?<!\\)\|', r'\|', pattern)
    if escaped != pattern:
        return escaped, True
    return pattern, False


@tool(
    name="search",
    description="Search files with Everything",
    schema={
        "type": "object",
        "properties": {
            "query_string": {
                "type": "string",
                "description": "Search query string"
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
        "required": [
            "query_string"
        ]
    }
)
def search(
    query_string: str,
    match_case: bool = False,
    match_path: bool = False,
    match_whole_word: bool = False,
    regex: bool = False,
    sort_type: int = 1,
    max_results: int = 10,
    return_properties=None
) -> str:
    """使用 Everything 搜索文件。

    Args:
        query_string: 搜索关键词。
        match_case: 是否区分大小写，默认 False。
        match_path: 是否匹配完整路径，默认 False。
        match_whole_word: 是否全词匹配，默认 False。
        regex: 是否启用正则表达式，默认 False。
        sort_type: 排序类型，默认 1 (名称升序)。
        max_results: 最大返回结果数，默认 10。
        return_properties: 控制返回的字段列表，支持数组或逗号分隔字符串。

    Returns:
        表格格式的搜索结果字符串。
    """
    try:
        from everytools import Search, SortType

        # 【猫娘修复】Issue 1: MCP 传输层将 integer/boolean 转为字符串，增加安全转换函数防底层 TypeError。【修改时间】：2026-05-15 17:40:00。
        sort_type = _safe_int(sort_type, 1)
        max_results = _safe_int(max_results, 10)
        match_case = _safe_bool(match_case, False)
        match_path = _safe_bool(match_path, False)
        match_whole_word = _safe_bool(match_whole_word, False)
        regex = _safe_bool(regex, False)

        # 【猫娘修复】Issue 2: return_properties 未做 split 容错，渲染异常。【修改时间】：2026-05-15 17:40:00。
        cols = _safe_list(return_properties, [
            "full_path",
            "size",
            "date_created"
        ])

        engine = Search(
            query_string=query_string,
            match_case=match_case,
            match_path=match_path,
            match_whole_word=match_whole_word,
            regex=regex,
            sort_type=SortType(sort_type),
            max_results=max_results
        )
        engine.execute()
        result_set = engine.get_results()
        
        # 【猫娘修改】：恢复原版逻辑，不强制切片，保留完整统计上下文。使用 list() 强转确保兼容性。【修改时间】：2026-05-15 17:40:00。
        results = list(result_set)
        
        # 构建字典列表，兼容 object 与 dict 混合结果
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

        title = f"搜索结果: {query_string} (返回 {len(dict_rows)} 条, 总计 {total} 条, 文件 {total_files}, 文件夹 {total_folders})"
        return _format_ascii_table(title, cols, dict_rows)

    except Exception as e:
        return f"Error: {e}"
