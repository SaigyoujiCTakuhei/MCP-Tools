"""
获取当前日期
（修正3：时间标准化为中国时区 Asia/Shanghai）
"""
import json

from Lib.base.base import tool

@tool(
    name="get_current_date",
    description="Get current date in China Standard Time (Asia/Shanghai timezone).",
    schema={
        "type": "object",
        "properties": {},
        "required": []
    }
)
def get_current_date() -> str:
    """
    获取当前日期（修正3：使用中国时区）
    """
    import datetime
    try:
        # 修正3：使用中国时区获取当前日期
        import zoneinfo
        shanghai_tz = zoneinfo.ZoneInfo("Asia/Shanghai")
        now = datetime.datetime.now(shanghai_tz)
        return now.strftime("%Y-%m-%d")
    except (ModuleNotFoundError, KeyError):
        # 回退到本地时区
        return str(datetime.date.today())
    except Exception as e:
        return f"Error: {e}"
