"""
网易云音乐基础控制模块
负责：启动应用、播放控制、音量调节、界面切换、喜欢歌曲等
"""
import os
import subprocess
import time
import logging
import webbrowser
from typing import Dict, Optional
from Lib.base.base import tool

# 尝试导入全局快捷键库
try:
    import pyautogui
    HOTKEY_AVAILABLE = True
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0.1
except ImportError:
    HOTKEY_AVAILABLE = False

# 尝试导入Windows窗口控制库
try:
    import win32gui
    import win32con
    WINDOW_CONTROL_AVAILABLE = True
except ImportError:
    WINDOW_CONTROL_AVAILABLE = False

logger = logging.getLogger(__name__)

DEFAULT_HOTKEYS = {
    "play_pause": "ctrl+alt+p",
    "previous": "ctrl+alt+left", 
    "next": "ctrl+alt+right",
    "volume_up": "ctrl+alt+up",
    "volume_down": "ctrl+alt+down",
    "mini_mode": "ctrl+alt+m",
    "like_song": "ctrl+alt+l",
    "lyrics": "ctrl+alt+d"
}

def get_platform() -> str:
    """获取当前操作系统平台"""
    import platform
    return platform.system().lower()

@tool(
    name="launch_netease_music",
    description="启动网易云音乐应用。支持 URL scheme 快速启动，可选自动最小化窗口。",
    schema={
        "type": "object",
        "properties": {
            "minimize_window": {"type": "boolean", "description": "是否自动最小化窗口（默认True）"}
        },
        "required": ["minimize_window"]
    }
)
def launch_netease_music(minimize_window: bool = True) -> dict:
    """启动网易云音乐应用"""
    try:
        logger.info("正在启动网易云音乐...")
        # 使用 orpheus:// 启动
        os.startfile("orpheus://")
        
        if minimize_window:
            time.sleep(1.5)
            # 尝试最小化窗口
            if WINDOW_CONTROL_AVAILABLE:
                def enum_windows_callback(hwnd, windows):
                    if win32gui.IsWindowVisible(hwnd):
                        window_title = win32gui.GetWindowText(hwnd)
                        if "网易云音乐" in window_title or "CloudMusic" in window_title:
                            windows.append(hwnd)
                    return True
                
                windows = []
                win32gui.EnumWindows(enum_windows_callback, windows)
                for hwnd in windows:
                    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                    logger.info(f"已最小化窗口: {hwnd}")
                    break
            else:
                logger.warning("窗口控制功能不可用，无法最小化窗口")
        
        return {
            "success": True,
            "message": "✅ 网易云音乐启动成功",
            "minimized": minimize_window
        }
    except Exception as e:
        logger.error(f"启动网易云音乐失败: {e}")
        return {"success": False, "error": str(e)}

@tool(
    name="control_playback",
    description="控制网易云音乐播放（通过全局快捷键）。支持：play_pause, previous, next。",
    schema={
        "type": "object",
        "properties": {
            "action": {"type": "string", "description": "播放控制动作 - play_pause(播放/暂停), previous(上一首), next(下一首)", "enum": ["play_pause", "previous", "next"]}
        },
        "required": ["action"]
    }
)
def control_playback(action: str = "play_pause") -> dict:
    """控制网易云音乐播放（全局快捷键）"""
    if not HOTKEY_AVAILABLE:
        return {"success": False, "error": "pyautogui 未安装，无法使用快捷键控制"}
    
    hotkey_map = {
        "play_pause": "ctrl+alt+p",
        "previous": "ctrl+alt+left", 
        "next": "ctrl+alt+right"
    }
    
    if action not in hotkey_map:
        return {"success": False, "error": f"无效的操作: {action}"}
    
    try:
        keys = hotkey_map[action].split("+")
        pyautogui.hotkey(*keys)
        logger.info(f"发送快捷键: {action}")
        return {"success": True, "message": f"✅ 播放控制成功: {action}"}
    except Exception as e:
        logger.error(f"播放控制失败: {e}")
        return {"success": False, "error": str(e)}

@tool(
    name="control_volume",
    description="控制网易云音乐音量（通过全局快捷键）。支持：volume_up, volume_down。",
    schema={
        "type": "object",
        "properties": {
            "action": {"type": "string", "description": "音量控制动作 - volume_up(音量加), volume_down(音量减)", "enum": ["volume_up", "volume_down"]}
        },
        "required": ["action"]
    }
)
def control_volume(action: str = "volume_up") -> dict:
    """控制网易云音乐音量（全局快捷键）"""
    if not HOTKEY_AVAILABLE:
        return {"success": False, "error": "pyautogui 未安装"}
    
    hotkey_map = {
        "volume_up": "ctrl+alt+up",
        "volume_down": "ctrl+alt+down"
    }
    
    if action not in hotkey_map:
        return {"success": False, "error": f"无效的操作: {action}"}
    
    try:
        keys = hotkey_map[action].split("+")
        pyautogui.hotkey(*keys)
        logger.info(f"发送快捷键: {action}")
        return {"success": True, "message": f"✅ 音量控制成功: {action}"}
    except Exception as e:
        logger.error(f"音量控制失败: {e}")
        return {"success": False, "error": str(e)}

@tool(
    name="toggle_mini_mode",
    description="切换网易云音乐迷你模式（通过全局快捷键）。",
    schema={
        "type": "object",
        "properties": {},
        "required": []
    }
)
def toggle_mini_mode() -> dict:
    """切换网易云音乐迷你模式"""
    if not HOTKEY_AVAILABLE:
        return {"success": False, "error": "pyautogui 未安装"}
    
    try:
        pyautogui.hotkey("ctrl", "alt", "m")
        return {"success": True, "message": "✅ 迷你模式切换成功"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@tool(
    name="like_current_song",
    description="喜欢当前播放的歌曲（通过全局快捷键）。",
    schema={
        "type": "object",
        "properties": {},
        "required": []
    }
)
def like_current_song() -> dict:
    """喜欢当前播放的歌曲"""
    if not HOTKEY_AVAILABLE:
        return {"success": False, "error": "pyautogui 未安装"}
    
    try:
        pyautogui.hotkey("ctrl", "alt", "l")
        return {"success": True, "message": "✅ 歌曲喜欢操作成功"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@tool(
    name="toggle_lyrics",
    description="打开/关闭歌词显示（通过全局快捷键）。",
    schema={
        "type": "object",
        "properties": {},
        "required": []
    }
)
def toggle_lyrics() -> dict:
    """打开/关闭歌词显示"""
    if not HOTKEY_AVAILABLE:
        return {"success": False, "error": "pyautogui 未安装"}
    
    try:
        pyautogui.hotkey("ctrl", "alt", "d")
        return {"success": True, "message": "✅ 歌词显示切换成功"}
    except Exception as e:
        return {"success": False, "error": str(e)}
