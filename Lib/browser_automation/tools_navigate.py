"""
导航与基础交互工具 (P0)
【猫娘修改】：navigate/click/fill/screenshot 核心页面操作
"""

import base64
from typing import Optional
from Lib.base.base import tool
from .browser_manager import manager


@tool(
    name="browser_navigate",
    description="导航至目标 URL，支持多等待策略与超时控制",
    schema={"type": "object", "properties": {
        "url": {"type": "string", "description": "目标地址"},
        "waitUntil": {"type": "string", "enum": ["load", "domcontentloaded", "networkidle", "commit"], "description": "加载完成条件"},
        "timeout": {"type": "number", "description": "导航超时 (ms)", "default": 30000}
    }, "required": ["url"]}
)
async def browser_navigate(url: str, waitUntil: str = "domcontentloaded", timeout: int = 30000):
    await manager._ensure_initialized()
    if not manager._page_pool:
        await manager._register_page(await manager._context.new_page())
    p = manager.get_active_page()
    await p.goto(url, wait_until=waitUntil, timeout=timeout)
    title = await p.title()
    return f"导航成功: {url} (标题: {title})"


@tool(
    name="browser_click",
    description="点击页面元素，支持强制点击与重复点击",
    schema={"type": "object", "properties": {
        "selector": {"type": "string", "description": "CSS 选择器"},
        "timeout": {"type": "number", "description": "等待元素超时 (ms)"},
        "force": {"type": "boolean", "description": "忽略遮挡强制点击"},
        "clickCount": {"type": "integer", "description": "点击次数"}
    }, "required": ["selector"]}
)
async def browser_click(selector: str, timeout: Optional[int] = None, force: bool = False, clickCount: int = 1):
    page = manager.get_active_page()
    await page.click(selector, timeout=timeout, force=force, click_count=clickCount)
    return f"点击成功: {selector}"


@tool(
    name="browser_fill",
    description="向输入框填入文本，支持异步等待与无阻塞模式",
    schema={"type": "object", "properties": {
        "selector": {"type": "string", "description": "输入框选择器"},
        "value": {"type": "string", "description": "填入内容"},
        "timeout": {"type": "number", "description": "等待元素超时 (ms)"},
        "noWaitAfter": {"type": "boolean", "description": "不等待页面跳转"}
    }, "required": ["selector", "value"]}
)
async def browser_fill(selector: str, value: str, timeout: Optional[int] = None, noWaitAfter: bool = False):
    page = manager.get_active_page()
    await page.fill(selector, value, timeout=timeout, no_wait_after=noWaitAfter)
    return f"填入成功: {selector} = {value}"


@tool(
    name="browser_screenshot",
    description="截取当前页/元素截图，返回 Base64 图片数据",
    schema={"type": "object", "properties": {
        "fullPage": {"type": "boolean", "description": "是否截取全页", "default": False},
        "selector": {"type": "string", "description": "指定元素选择器 (可选)"}
    }}
)
async def browser_screenshot(fullPage: bool = False, selector: Optional[str] = None):
    page = manager.get_active_page()
    target = page.locator(selector) if selector else page
    img = await target.screenshot(full_page=fullPage, type="png")
    return f"data:image/png;base64,{base64.b64encode(img).decode('utf-8')}"
