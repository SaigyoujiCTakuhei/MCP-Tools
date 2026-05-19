"""
Cookie 与存储管理工具 (P3)
【猫娘修改】：get_cookies/set_cookies/clear_cookies/storage_state 会话持久化
"""

import json
from typing import Optional
from pathlib import Path
from Lib.base.base import tool
from .browser_manager import manager


@tool(
    name="browser_get_cookies",
    description="获取当前域名下的所有 Cookie",
    schema={"type": "object", "properties": {
        "urls": {"type": "array", "items": {"type": "string"}, "description": "指定域名列表 (可选，留空获取全部)"}
    }}
)
async def browser_get_cookies(urls: Optional[list] = None):
    cookies = await manager.context.cookies(urls or [])
    return json.dumps(cookies, ensure_ascii=False)


@tool(
    name="browser_set_cookies",
    description="设置 Cookie (用于登录态注入)",
    schema={"type": "object", "properties": {
        "cookies": {"type": "array", "items": {"type": "object", "properties": {
            "name": {"type": "string"}, "value": {"type": "string"}, "domain": {"type": "string"},
            "path": {"type": "string"}, "expires": {"type": "number"}, "httpOnly": {"type": "boolean"},
            "secure": {"type": "boolean"}, "sameSite": {"type": "string", "enum": ["Strict", "Lax", "None"]}
        }}, "required": ["name", "value"], "description": "Cookie 数组"}
    }, "required": ["cookies"]}
)
async def browser_set_cookies(cookies: list):
    await manager.context.add_cookies(cookies)
    return f"已注入 {len(cookies)} 个 Cookie"


@tool(
    name="browser_clear_cookies",
    description="清空当前域名下的所有 Cookie",
    schema={"type": "object", "properties": {
        "urls": {"type": "array", "items": {"type": "string"}, "description": "指定域名列表 (可选，留空清空全部)"}
    }}
)
async def browser_clear_cookies(urls: Optional[list] = None):
    await manager.context.clear_cookies(urls or [])
    return "Cookie 已清空"


@tool(
    name="browser_storage_state",
    description="获取或保存浏览器存储状态 (包含 cookies/localStorage/sessionStorage)",
    schema={"type": "object", "properties": {
        "filePath": {"type": "string", "description": "保存路径 (可选，不传则仅返回 JSON 字符串)"}
    }}
)
async def browser_storage_state(filePath: Optional[str] = None):
    state = await manager.context.storage_state()
    if filePath:
        Path(filePath).parent.mkdir(parents=True, exist_ok=True)
        with open(filePath, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        return f"存储状态已保存至: {filePath}"
    return json.dumps(state, ensure_ascii=False)
