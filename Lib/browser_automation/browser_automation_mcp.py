"""
Browser Automation MCP Server - Main Entry
【猫娘修改】：主入口文件，负责工具模块导入与信号处理
"""

import asyncio
import signal

# ==================== 导入所有工具模块 ====================
from .tools_navigate import browser_navigate, browser_click, browser_fill, browser_screenshot
from .tools_environment import browser_resize, browser_set_ua, browser_close
from .tools_network import browser_http_get, browser_http_post, browser_expect_response, browser_assert_response
from .tools_debug import browser_console_logs, browser_get_visible_html, browser_save_as_pdf
from .tools_interaction import browser_press_key, browser_drag, browser_evaluate
from .tools_cookies import browser_get_cookies, browser_set_cookies, browser_clear_cookies, browser_storage_state

# ==================== 信号处理钩子 ====================
from .browser_manager import manager

async def shutdown():
    await manager.close()
    exit(0)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, lambda: asyncio.ensure_future(shutdown()))
    loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.ensure_future(shutdown()))
    print("Browser Automation Module Loaded into ToolRegistry (Modular Structure).")
