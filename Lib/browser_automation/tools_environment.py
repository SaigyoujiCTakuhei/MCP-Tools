"""
环境配置与页面管理工具 (P1)
【猫娘修改】：resize/set_ua/close 设备模拟与生命周期管理
"""

from typing import Optional
from Lib.base.base import tool
from .browser_manager import manager


@tool(
    name="browser_resize",
    description="调整视口或切换设备预设 (移动端/平板/桌面)",
    schema={"type": "object", "properties": {
        "device": {"type": "string", "description": "设备预设名称 (如 iPhone 13, Pixel 7, Desktop Chrome)"},
        "width": {"type": "number", "description": "手动宽度 (px)"},
        "height": {"type": "number", "description": "手动高度 (px)"}
    }}
)
async def browser_resize(device: Optional[str] = None, width: Optional[float] = None, height: Optional[float] = None):
    page = manager.get_active_page()
    presets = {
        "iPhone 13": {"width": 390, "height": 844},
        "Pixel 7": {"width": 412, "height": 915},
        "Desktop Chrome": {"width": 1280, "height": 720}
    }
    if device:
        settings = presets.get(device, {"width": width, "height": height})
    else:
        settings = {"width": width or 1280, "height": height or 720}
    await page.set_viewport_size(settings)
    return f"已切换至设备/视口: {device or settings}"


@tool(
    name="browser_set_ua",
    description="动态覆盖浏览器 User-Agent",
    schema={"type": "object", "properties": {
        "userAgent": {"type": "string", "description": "自定义 UA 字符串"}
    }, "required": ["userAgent"]}
)
async def browser_set_ua(userAgent: str):
    page = manager.get_active_page()
    await page.set_extra_http_headers({"User-Agent": userAgent})
    return "User-Agent 已更新"


@tool(
    name="browser_close",
    description="显式关闭浏览器上下文，释放系统资源",
    schema={"type": "object", "properties": {}}
)
async def browser_close():
    await manager.close()
    return "浏览器上下文已安全释放"
