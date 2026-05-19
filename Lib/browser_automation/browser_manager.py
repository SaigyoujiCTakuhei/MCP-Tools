"""
Browser Manager - 核心状态管理模块
【猫娘修改】：单例模式管理 Browser/Context/PagePool，支持异步初始化与资源释放
"""

import asyncio
from typing import Optional, Dict
from playwright.async_api import async_playwright, Browser, BrowserContext, Page


class BrowserManager:
    def __init__(self):
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page_pool: Dict[str, Page] = {}
        self._response_waits: Dict[str, asyncio.Future] = {}
        self._console_logs: list = []
        self._lock = asyncio.Lock()

    async def _ensure_initialized(self):
        if self._browser is None or not self._browser.is_connected():
            playwright = await async_playwright().start()
            self._browser = await playwright.chromium.launch(headless=False)
            self._context = await self._browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            self._context.on("console", self._handle_console)
            self._context.on("page", self._on_new_page)

    def _handle_console(self, msg):
        log_entry = f"[{msg.type}] {msg.text}"
        self._console_logs.append(log_entry)
        if len(self._console_logs) > 500:
            self._console_logs.pop(0)

    def _on_new_page(self, page: Page):
        asyncio.get_event_loop().create_task(self._register_page(page))

    async def _register_page(self, page: Page):
        await page.bring_to_front()
        async with self._lock:
            pid = f"page_{id(page)}"
            self._page_pool[pid] = page

    def get_active_page(self) -> Page:
        if not self._page_pool:
            raise RuntimeError("No active page. Use navigate first.")
        return list(self._page_pool.values())[-1]

    @property
    def context(self) -> BrowserContext:
        if not self._context:
            raise RuntimeError("Browser context not initialized. Call navigate first.")
        return self._context

    async def close(self):
        async with self._lock:
            if self._browser:
                await self._browser.close()
                self._browser = None
                self._context = None
                self._page_pool.clear()
                self._response_waits.clear()
                self._console_logs.clear()

# 全局单例
manager = BrowserManager()
