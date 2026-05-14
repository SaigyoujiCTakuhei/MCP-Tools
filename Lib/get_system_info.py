"""
获取系统信息
（修正3：时间标准化为中国时区）
"""
import json

from Lib.base import tool

@tool(
    name="get_system_info",
    description="Get system information including platform, Python version, and current time (China Standard Time).",
    schema={
        "type": "object",
        "properties": {},
        "required": []
    }
)
def get_system_info() -> str:
    """
    获取系统信息（修正3：时间使用中国时区）
    """
    import platform
    import os
    import datetime

    try:
        # 修正3：使用中国时区
        import zoneinfo
        shanghai_tz = zoneinfo.ZoneInfo("Asia/Shanghai")
        now = datetime.datetime.now(shanghai_tz)
        current_time = now.isoformat()
    except (ModuleNotFoundError, KeyError):
        current_time = datetime.datetime.now().isoformat()

    return json.dumps({
        "platform": platform.platform(),
        "python": platform.python_version(),
        "host": platform.node(),
        "cwd": os.getcwd(),
        "timezone": "Asia/Shanghai",  # 修正3：标明时区
        "time": current_time
    }, indent=2, ensure_ascii=False)
