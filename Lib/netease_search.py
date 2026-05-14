"""
网易云音乐搜索模块
负责：搜索歌曲、搜索歌单并播放
"""
import os
import requests
import json
import base64
import logging
from typing import Optional
from Lib.base import tool

logger = logging.getLogger(__name__)

def search_netease_music(song_name: str) -> Optional[tuple]:
    """搜索网易云音乐并获取歌曲ID"""
    try:
        url = "http://music.163.com/api/search/get/web"
        params = {
            'csrf_token': '',
            's': song_name,
            'type': 1,
            'offset': 0,
            'total': 'true',
            'limit': 1
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Referer': 'http://music.163.com/'
        }
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200 and 'result' in data:
                songs = data['result'].get('songs', [])
                if songs:
                    song = songs[0]
                    return (song['id'], song['name'], song['artists'][0]['name'] if song['artists'] else '未知')
    except Exception as e:
        logger.error(f"搜索歌曲失败: {e}")
    return None

def search_netease_playlist(playlist_name: str) -> Optional[tuple]:
    """搜索网易云音乐歌单并获取歌单ID"""
    try:
        url = "http://music.163.com/api/search/get/web"
        params = {
            'csrf_token': '',
            's': playlist_name,
            'type': 1000,  # 歌单搜索
            'offset': 0,
            'total': 'true',
            'limit': 1
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Referer': 'http://music.163.com/'
        }
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200 and 'result' in data:
                playlists = data['result'].get('playlists', [])
                if playlists:
                    pl = playlists[0]
                    return (str(pl['id']), pl['name'])
    except Exception as e:
        logger.error(f"搜索歌单失败: {e}")
    return None

def generate_play_url(item_id: int, type: str = "song") -> Optional[str]:
    """生成播放URL scheme"""
    try:
        cmd = {"type": type, "id": str(item_id), "cmd": "play"}
        json_str = json.dumps(cmd, separators=(',', ':'))
        encoded = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
        return f"orpheus://{encoded}"
    except Exception as e:
        logger.error(f"生成URL失败: {e}")
        return None

@tool(
    name="search_and_play_song",
    description="搜索歌曲并直接播放。支持自然语言搜索。",
    schema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "搜索关键词（歌曲名或歌曲名+歌手）"},
            "minimize_window": {"type": "boolean", "description": "是否自动最小化窗口"}
        },
        "required": ["query"]
    }
)
def search_and_play_song(query: str, minimize_window: bool = True) -> dict:
    """搜索歌曲并直接播放"""
    try:
        result = search_netease_music(query)
        if not result:
            return {"success": False, "error": "未找到歌曲"}
        
        song_id, song_name, artist = result
        play_url = generate_play_url(song_id)
        
        if play_url:
            os.startfile(play_url)
            return {
                "success": True,
                "message": f"✅ 正在播放: 《{song_name}》- {artist}",
                "song": song_name,
                "artist": artist
            }
        else:
            return {"success": False, "error": "生成播放URL失败"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@tool(
    name="search_and_play_playlist",
    description="搜索歌单并直接播放。",
    schema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "搜索关键词（歌单名称）"},
            "minimize_window": {"type": "boolean", "description": "是否自动最小化窗口"}
        },
        "required": ["query"]
    }
)
def search_and_play_playlist(query: str, minimize_window: bool = True) -> dict:
    """搜索歌单并直接播放"""
    try:
        result = search_netease_playlist(query)
        if not result:
            return {"success": False, "error": "未找到歌单"}
        
        playlist_id, playlist_name = result
        play_url = generate_play_url(playlist_id, type="playlist")
        
        if play_url:
            os.startfile(play_url)
            return {
                "success": True,
                "message": f"✅ 正在播放歌单: 《{playlist_name}》",
                "playlist": playlist_name
            }
        else:
            return {"success": False, "error": "生成播放URL失败"}
    except Exception as e:
        return {"success": False, "error": str(e)}
