"""
番茄小说搜索相关工具
"""
from Lib.base import tool
from Lib.fanqie_api import client


@tool(
    name="fanqie_search_books",
    description="搜索番茄小说平台上的书籍、听书、漫画或短剧",
    schema={
        "type": "object",
        "properties": {
            "key": {"type": "string", "description": "搜索关键词"},
            "tab_type": {"type": "integer", "description": "内容类型：3=小说, 2=听书, 8=漫画, 11=短剧", "default": 3},
            "offset": {"type": "integer", "description": "分页偏移量", "default": 0}
        },
        "required": ["key"]
    }
)
def fanqie_search_books(key: str, tab_type: int = 3, offset: int = 0) -> dict:
    if not key:
        raise ValueError("搜索关键词不能为空")
    results = client.search_books(key, tab_type, offset)
    return {"keyword": key, "tab_type": tab_type, "offset": offset, "results": results}