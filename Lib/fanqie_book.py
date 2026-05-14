"""
番茄小说书籍详情与目录相关工具
"""
from Lib.base import tool
from Lib.fanqie_api import client


@tool(
    name="fanqie_get_book_detail",
    description="获取指定书籍的详细信息",
    schema={
        "type": "object",
        "properties": {
            "book_id": {"type": "string", "description": "书籍ID"}
        },
        "required": ["book_id"]
    }
)
def fanqie_get_book_detail(book_id: str) -> dict:
    if not book_id:
        raise ValueError("书籍ID不能为空")
    detail = client.get_book_detail(book_id)
    return {"book_id": book_id, "detail": detail}


@tool(
    name="fanqie_get_book_directory",
    description="获取书籍的完整章节目录列表",
    schema={
        "type": "object",
        "properties": {
            "book_id": {"type": "string", "description": "书籍ID"}
        },
        "required": ["book_id"]
    }
)
def fanqie_get_book_directory(book_id: str) -> dict:
    if not book_id:
        raise ValueError("书籍ID不能为空")
    directory = client.get_book_directory(book_id)
    return {"book_id": book_id, "directory": directory}


@tool(
    name="fanqie_get_simple_directory",
    description="获取书籍的简化目录信息",
    schema={
        "type": "object",
        "properties": {
            "book_id": {"type": "string", "description": "书籍ID"}
        },
        "required": ["book_id"]
    }
)
def fanqie_get_simple_directory(book_id: str) -> dict:
    if not book_id:
        raise ValueError("书籍ID不能为空")
    simple_dir = client.get_simple_directory(book_id)
    return {"book_id": book_id, "simple_directory": simple_dir}