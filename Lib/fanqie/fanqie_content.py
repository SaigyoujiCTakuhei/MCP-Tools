"""
番茄小说内容获取相关工具
"""
from Lib.base.base import tool
from Lib.fanqie_api import client


@tool(
    name="fanqie_get_chapter_content",
    description="获取指定章节的文本内容（简化接口）",
    schema={
        "type": "object",
        "properties": {
            "item_id": {"type": "string", "description": "章节ID"}
        },
        "required": ["item_id"]
    }
)
def fanqie_get_chapter_content(item_id: str) -> dict:
    if not item_id:
        raise ValueError("章节ID不能为空")
    content = client.get_chapter(item_id)
    return {"item_id": item_id, "content": content}


@tool(
    name="fanqie_get_content",
    description="统一的内容获取接口，支持小说、听书、短剧、漫画及批量获取",
    schema={
        "type": "object",
        "properties": {
            "tab": {"type": "string", "description": "内容类型：novel, audiobook, short drama, comic, batch"},
            "item_id": {"type": "string", "description": "单个章节/视频/漫画 ID"},
            "item_ids": {"type": "string", "description": "多个章节 ID，逗号分隔"},
            "book_id": {"type": "string", "description": "书籍 ID"},
            "show_html": {"type": "string", "description": "漫画是否返回 HTML 格式 (0 或 1)", "enum": ["0", "1"]},
            "tone_id": {"type": "string", "description": "有声书音色 ID"}
        },
        "required": ["tab"]
    }
)
def fanqie_get_content(tab: str, item_id: str = None, item_ids: str = None, 
                       book_id: str = None, show_html: str = None, tone_id: str = None) -> dict:
    if not tab:
        raise ValueError("内容类型不能为空")
    
    if tab != "batch" and not item_id:
        raise ValueError("需要提供 item_id 参数")
    if tab == "batch" and (not item_ids or not book_id):
        raise ValueError("批量获取需要提供 item_ids 和 book_id 参数")
        
    content = client.get_content(tab, item_id, item_ids, book_id, show_html, tone_id)
    return {"tab": tab, "item_id": item_id, "item_ids": item_ids, "book_id": book_id, "content": content}