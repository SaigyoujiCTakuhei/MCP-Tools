"""
番茄小说 MCP 服务器配置模块
"""

# API 基础 URL
FANQIE_API_BASE: str = "http://103.236.91.147:9999"

# 默认请求头
FANQIE_HEADERS: dict = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
}

# 默认超时时间（秒）
DEFAULT_TIMEOUT: int = 60