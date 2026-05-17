"""
网易云音乐配置模块
负责：获取配置信息、控制器状态
"""
import os
import logging
from typing import Optional
from Lib.base.base import tool

logger = logging.getLogger(__name__)

@tool(
    name="get_netease_config",
    description="获取网易云音乐配置信息，验证路径是否有效。",
    schema={
        "type": "object",
        "properties": {},
        "required": []
    }
)
def get_netease_config() -> dict:
    """获取网易云音乐配置信息"""
    # 这里可以读取 netease_config.json，目前使用硬编码默认路径
    netease_path = os.environ.get("NETEASE_MUSIC_PATH", "")
    chromedriver_path = os.environ.get("CHROMEDRIVER_PATH", "")
    
    netease_status = "未配置"
    chromedriver_status = "未配置"
    
    if netease_path:
        netease_status = "✅ 有效" if os.path.exists(netease_path) else "❌ 无效"
    
    if chromedriver_path:
        chromedriver_status = "✅ 有效" if os.path.exists(chromedriver_path) else "❌ 无效"
    
    return {
        "success": True,
        "config": {
            "netease_music_path": netease_path,
            "path_status": netease_status,
            "chromedriver_path": chromedriver_path,
            "chromedriver_status": chromedriver_status
        },
        "message": "✅ 配置信息获取成功"
    }

@tool(
    name="get_controller_info",
    description="获取控制器信息和支持的功能列表。",
    schema={
        "type": "object",
        "properties": {},
        "required": []
    }
)
def get_controller_info() -> dict:
    """获取控制器信息"""
    try:
        import pyautogui
        hotkey_avail = True
    except:
        hotkey_avail = False
    
    return {
        "success": True,
        "data": {
            "server_name": "网易云音乐控制器",
            "hotkey_available": hotkey_avail,
            "supported_actions": ["play_pause", "previous", "next", "volume_up", "volume_down", "mini_mode", "like_song", "lyrics"]
        },
        "message": "✅ 控制器信息获取成功"
    }
