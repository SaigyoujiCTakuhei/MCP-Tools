"""
交互与执行工具 (P2)
【猫娘修改】：press_key/drag/evaluate 键盘/拖拽/JS 执行
"""

import json
from typing import Optional
from Lib.base.base import tool
from .browser_manager import manager


@tool(
    name="browser_press_key",
    description="模拟键盘按键事件 (回车/方向键/组合键)",
    schema={"type": "object", "properties": {
        "key": {"type": "string", "description": "按键名称 (如 Enter, ArrowDown, Ctrl+A)"},
        "selector": {"type": "string", "description": "聚焦目标选择器 (可选)"}
    }, "required": ["key"]}
)
async def browser_press_key(key: str, selector: Optional[str] = None):
    page = manager.get_active_page()
    if selector:
        await page.fill(selector, "")
    await page.keyboard.press(key)
    return f"按键触发: {key}"


@tool(
    name="browser_drag",
    description="拖拽元素至目标位置",
    schema={"type": "object", "properties": {
        "sourceSelector": {"type": "string", "description": "源元素选择器"},
        "targetSelector": {"type": "string", "description": "目标元素选择器"}
    }, "required": ["sourceSelector", "targetSelector"]}
)
async def browser_drag(sourceSelector: str, targetSelector: str):
    page = manager.get_active_page()
    await page.drag_and_drop(sourceSelector, targetSelector)
    return f"拖拽完成: {sourceSelector} -> {targetSelector}"


@tool(
    name="browser_evaluate",
    description="在当前页面上下文执行任意 JavaScript 代码",
    schema={"type": "object", "properties": {
        "expression": {"type": "string", "description": "JS 表达式/函数"}
    }, "required": ["expression"]}
)
async def browser_evaluate(expression: str):
    page = manager.get_active_page()
    res = await page.evaluate(expression)
    return str(json.dumps(res, ensure_ascii=False, default=str))
