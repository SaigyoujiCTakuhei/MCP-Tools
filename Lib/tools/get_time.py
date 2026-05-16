"""
获取当前日期和时间
（修正3：时间标准化为中国时区 Asia/Shanghai）
"""
import json

from Lib.base.base import tool

@tool(
    name="get_time",
    description="Get the current date and time. Default timezone is Asia/Shanghai (China Standard Time).",
    schema={
        "type": "object",
        "properties": {
            "timezone": {
                "type": "string",
                "default": "Asia/Shanghai",
                "description": "Timezone identifier, default is Asia/Shanghai (China Standard Time)"
            }
        },
        "required": []
    }
)
def get_time(timezone: str = "Asia/Shanghai") -> str:
    """
    获取当前时间（修正3：默认使用中国时区）
    """
    import datetime
    try:
        # 修正3：默认使用中国时区，如果用户未指定
        if timezone == "UTC":
            now = datetime.datetime.now(datetime.timezone.utc)
        else:
            try:
                import zoneinfo
                now = datetime.datetime.now(zoneinfo.ZoneInfo(timezone))
            except (ModuleNotFoundError, KeyError):
                # 回退到 UTC（修正3：降级处理）
                now = datetime.datetime.now(datetime.timezone.utc)
        return now.isoformat()
    except Exception as e:
        return f"Error: {e}"
