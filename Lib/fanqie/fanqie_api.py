"""
番茄小说 API 客户端封装
"""
import requests
from Lib.base.base import tool
import Lib.fanqie_config as fanqie_config


class FanQieAPIClient:
    """番茄小说 API 客户端单例"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.base_url = fanqie_config.FANQIE_API_BASE
        self.session.headers.update(fanqie_config.FANQIE_HEADERS)
        self.session.timeout = fanqie_config.DEFAULT_TIMEOUT

    def _request(self, method: str, endpoint: str, params: dict = None) -> any:
        """发送 HTTP 请求并处理标准响应"""
        url = f"{self.session.base_url}/{endpoint.lstrip('/')}"
        try:
            resp = self.session.request(method, url, params=params, timeout=self.session.timeout)
            resp.raise_for_status()
            data = resp.json()
            
            code = data.get("code")
            if code == 200:
                return data.get("data")
            elif code == 403:
                raise Exception("未授权或授权已过期")
            elif code == 404:
                raise Exception("资源不存在")
            elif code == 400:
                raise Exception(f"请求参数错误: {data.get('message', '')}")
            elif code == 500:
                raise Exception("服务器内部错误")
            else:
                raise Exception(f"API返回错误: {data.get('message', 'Unknown')} (code: {code})")
        except requests.RequestException as e:
            raise Exception(f"网络请求失败: {e}")

    def search_books(self, key: str, tab_type: int = 3, offset: int = 0) -> list:
        return self._request("GET", "/api/search", {"key": key, "tab_type": tab_type, "offset": offset})

    def get_book_detail(self, book_id: str) -> dict:
        return self._request("GET", "/api/detail", {"book_id": book_id})

    def get_book_directory(self, book_id: str) -> dict:
        return self._request("GET", "/api/book", {"book_id": book_id})

    def get_simple_directory(self, book_id: str) -> dict:
        return self._request("GET", "/api/directory", {"fq_id": book_id})

    def get_content(self, tab: str, item_id: str = None, item_ids: str = None, 
                    book_id: str = None, show_html: str = None, tone_id: str = None) -> any:
        params = {"tab": tab}
        if item_id: params["item_id"] = item_id
        if item_ids: params["item_ids"] = item_ids
        if book_id: params["book_id"] = book_id
        if show_html: params["show_html"] = show_html
        if tone_id: params["tone_id"] = tone_id
        return self._request("GET", "/api/content", params)

    def get_chapter(self, item_id: str) -> str:
        return self._request("GET", "/api/chapter", {"item_id": item_id})

    def get_comments(self, book_id: str, count: int = 20, offset: int = 0) -> list:
        return self._request("GET", "/api/comment", {"book_id": book_id, "count": count, "offset": offset})

    def get_device_pool_status(self) -> dict:
        return self._request("GET", "/api/device/pool")

    def register_device(self, platform: str = "android") -> dict:
        return self._request("GET", "/api/device/register", {"platform": platform})

    def get_device_status(self, platform: str = "android") -> dict:
        return self._request("GET", "/api/device/status", {"platform": platform})


# 模块级单例客户端
client = FanQieAPIClient()