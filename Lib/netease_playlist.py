"""
网易云音乐歌单管理模块
负责：管理用户自定义歌单（增删查）
"""
import json
import os
import logging
from typing import Optional
from Lib.base import tool

logger = logging.getLogger(__name__)

PLAYLISTS_FILE = "playlists.json"

def load_playlists() -> dict:
    """加载歌单配置"""
    if os.path.exists(PLAYLISTS_FILE):
        try:
            with open(PLAYLISTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"systemPlaylists": {}, "userPlaylists": {}}
    return {"systemPlaylists": {}, "userPlaylists": {}}

def save_playlists(data: dict) -> bool:
    """保存歌单配置"""
    try:
        with open(PLAYLISTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"保存歌单失败: {e}")
        return False

@tool(
    name="manage_custom_playlists",
    description="管理用户自定义歌单。支持 list, add, remove 操作。",
    schema={
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["list", "add", "remove"], "description": "操作类型"},
            "playlist_name": {"type": "string", "description": "歌单名称"},
            "playlist_id": {"type": "string", "description": "歌单ID（add时需要）"},
            "description": {"type": "string", "description": "歌单描述"}
        },
        "required": ["action"]
    }
)
def manage_custom_playlists(action: str, playlist_name: str = "", playlist_id: str = "", description: str = "") -> dict:
    """管理用户自定义歌单"""
    try:
        if action == "list":
            data = load_playlists()
            return {
                "success": True,
                "data": data,
                "message": "✅ 获取歌单列表成功"
            }
        elif action == "add":
            if not playlist_name or not playlist_id:
                return {"success": False, "error": "添加歌单需要提供名称和ID"}
            
            data = load_playlists()
            # 简单去重检查（实际应检查ID）
            if playlist_name in data.get("userPlaylists", {}):
                return {"success": False, "error": "歌单名称已存在"}
            
            if "userPlaylists" not in data:
                data["userPlaylists"] = {}
            
            data["userPlaylists"][playlist_name] = {
                "id": playlist_id,
                "name": playlist_name,
                "description": description
            }
            
            if save_playlists(data):
                return {"success": True, "message": f"✅ 成功添加歌单: {playlist_name}"}
            else:
                return {"success": False, "error": "保存失败"}
        elif action == "remove":
            if not playlist_name:
                return {"success": False, "error": "删除歌单需要提供名称"}
            
            data = load_playlists()
            if playlist_name in data.get("userPlaylists", {}):
                del data["userPlaylists"][playlist_name]
                if save_playlists(data):
                    return {"success": True, "message": f"✅ 成功删除歌单: {playlist_name}"}
                else:
                    return {"success": False, "error": "保存失败"}
            else:
                return {"success": False, "error": "未找到该歌单"}
        else:
            return {"success": False, "error": f"不支持的操作: {action}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
