"""
番茄小说评论与设备管理相关工具
"""
from Lib.base import tool
from Lib.fanqie_api import client


@tool(
    name="fanqie_get_comments",
    description="获取书籍或内容的评论列表，支持分页",
    schema={
        "type": "object",
        "properties": {
            "book_id": {"type": "string", "description": "书籍ID"},
            "count": {"type": "integer", "description": "每页数量", "default": 20},
            "offset": {"type": "integer", "description": "偏移量", "default": 0}
        },
        "required": ["book_id"]
    }
)
def fanqie_get_comments(book_id: str, count: int = 20, offset: int = 0) -> dict:
    if not book_id:
        raise ValueError("书籍ID不能为空")
    comments = client.get_comments(book_id, count, offset)
    return {"book_id": book_id, "count": count, "offset": offset, "comments": comments}


@tool(
    name="fanqie_get_device_pool_status",
    description="查看设备池的整体状态",
    schema={"type": "object", "properties": {}}
)
def fanqie_get_device_pool_status() -> dict:
    status = client.get_device_pool_status()
    return {"device_pool_status": status}


@tool(
    name="fanqie_register_device",
    description="注册新设备到设备池",
    schema={
        "type": "object",
        "properties": {
            "platform": {"type": "string", "description": "平台类型：android 或 ios", "default": "android"}
        }
    }
)
def fanqie_register_device(platform: str = "android") -> dict:
    result = client.register_device(platform)
    return {"platform": platform, "registration_result": result}


@tool(
    name="fanqie_get_device_status",
    description="查看指定平台的设备状态",
    schema={
        "type": "object",
        "properties": {
            "platform": {"type": "string", "description": "平台类型：android 或 ios", "default": "android"}
        }
    }
)
def fanqie_get_device_status(platform: str = "android") -> dict:
    status = client.get_device_status(platform)
    return {"platform": platform, "device_status": status}