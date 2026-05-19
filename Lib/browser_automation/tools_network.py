"""
网络请求与响应监听工具 (P2)
【猫娘修改】：http_get/post/expect_response/assert_response 接口联动
"""

import asyncio
import json
import httpx
from typing import Optional
from Lib.base.base import tool
from .browser_manager import manager


@tool(
    name="browser_http_get",
    description="发起异步 HTTP GET 请求",
    schema={"type": "object", "properties": {
        "url": {"type": "string", "description": "请求地址"},
        "headers": {"type": "object", "description": "自定义请求头"},
        "token": {"type": "string", "description": "Bearer Token"}
    }, "required": ["url"]}
)
async def browser_http_get(url: str, headers: Optional[dict] = None, token: Optional[str] = None):
    hdrs = headers or {}
    if token:
        hdrs["Authorization"] = f"Bearer {token}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=hdrs, timeout=10.0)
        return json.dumps({"status": resp.status_code, "body": resp.text[:2000]}, ensure_ascii=False)


@tool(
    name="browser_http_post",
    description="发起异步 HTTP POST 请求",
    schema={"type": "object", "properties": {
        "url": {"type": "string", "description": "请求地址"},
        "body": {"type": "string", "description": "请求体 (JSON/表单)"},
        "headers": {"type": "object", "description": "自定义请求头"},
        "token": {"type": "string", "description": "Bearer Token"}
    }, "required": ["url", "body"]}
)
async def browser_http_post(url: str, body: str, headers: Optional[dict] = None, token: Optional[str] = None):
    hdrs = headers or {}
    if token:
        hdrs["Authorization"] = f"Bearer {token}"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=hdrs, content=body, timeout=10.0)
        return json.dumps({"status": resp.status_code, "body": resp.text[:2000]}, ensure_ascii=False)


@tool(
    name="browser_expect_response",
    description="开始监听指定 URL 的网络响应",
    schema={"type": "object", "properties": {
        "id": {"type": "string", "description": "监听会话唯一 ID"},
        "urlPattern": {"type": "string", "description": "URL 匹配模式/正则"}
    }, "required": ["id", "urlPattern"]}
)
async def browser_expect_response(id: str, urlPattern: str):
    page = manager.get_active_page()
    future = asyncio.get_event_loop().create_future()
    manager._response_waits[id] = future

    async def handler(route):
        resp = await route.fetch()
        await route.continue_()
        if not future.done():
            future.set_result(await resp.text())

    await page.route(urlPattern, handler)
    return f"开始监听响应: {urlPattern} (ID: {id})"


@tool(
    name="browser_assert_response",
    description="等待并验证已监听的响应结果",
    schema={"type": "object", "properties": {
        "id": {"type": "string", "description": "对应 expect_response 的 ID"}
    }, "required": ["id"]}
)
async def browser_assert_response(id: str):
    if id not in manager._response_waits:
        raise ValueError("未找到对应的响应监听 ID")
    resp = await manager._response_waits.pop(id)
    return f"响应捕获成功 (长度: {len(resp)})"
