"""
调试与导出工具 (P2)
【猫娘修改】：console_logs/get_visible_html/save_as_pdf 控制台与 DOM 操作
"""

import json
from typing import Optional
from Lib.base.base import tool
from .browser_manager import manager


@tool(
    name="browser_console_logs",
    description="获取浏览器控制台日志，支持过滤与清空",
    schema={"type": "object", "properties": {
        "type": {"type": "string", "enum": ["all", "error", "warning", "log", "info", "debug"], "default": "all"},
        "limit": {"type": "integer", "description": "返回条数限制"},
        "clear": {"type": "boolean", "description": "获取后清空缓存"}
    }}
)
async def browser_console_logs(type: str = "all", limit: Optional[int] = None, clear: bool = False):
    logs = manager._console_logs
    if type != "all":
        logs = [l for l in logs if type in l]
    if limit:
        logs = logs[-limit:]
    if clear:
        manager._console_logs.clear()
    return "\n".join(logs) if logs else "无匹配日志"


@tool(
    name="browser_get_visible_html",
    description="提取页面可见 DOM 结构，支持清洗脚本/样式/注释",
    schema={"type": "object", "properties": {
        "selector": {"type": "string", "description": "限定容器选择器"},
        "removeScripts": {"type": "boolean", "description": "移除 script 标签"},
        "removeStyles": {"type": "boolean", "description": "移除 style 标签"},
        "minify": {"type": "boolean", "description": "压缩输出"}
    }}
)
async def browser_get_visible_html(selector: Optional[str] = None, removeScripts: bool = False, removeStyles: bool = False, minify: bool = False):
    page = manager.get_active_page()
    html = await page.inner_html(selector) if selector else await page.content()
    if removeScripts:
        html = html.replace("<script>", "").replace("</script>", "")
    if removeStyles:
        html = html.replace("<style>", "").replace("</style>", "")
    if minify:
        html = " ".join(html.split())
    return html[:50000]


@tool(
    name="browser_save_as_pdf",
    description="将当前页导出为 PDF 文件，支持格式与边距配置",
    schema={"type": "object", "properties": {
        "outputPath": {"type": "string", "description": "保存路径"},
        "format": {"type": "string", "description": "纸张格式 (A4/Letter)"},
        "printBackground": {"type": "boolean", "description": "打印背景图"},
        "margin": {"type": "object", "properties": {
            "top": {"type": "string"}, "right": {"type": "string"},
            "bottom": {"type": "string"}, "left": {"type": "string"}
        }}
    }, "required": ["outputPath"]}
)
async def browser_save_as_pdf(outputPath: str, format: Optional[str] = None, printBackground: bool = False, margin: Optional[dict] = None):
    page = manager.get_active_page()
    kwargs = {"output_path": outputPath}
    if format:
        kwargs["format"] = format
    kwargs["print_background"] = printBackground
    if margin:
        kwargs["margin"] = margin
    await page.pdf(**kwargs)
    return f"PDF 已保存: {outputPath}"
