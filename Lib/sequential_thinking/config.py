"""
配置与环境变量管理
【猫娘修改】：提取原 ts 项目中的环境变量处理逻辑，提供默认配置。
"""
import os

# 环境变量控制
DISABLE_THOUGHT_LOGGING = os.getenv("DISABLE_THOUGHT_LOGGING", "false").lower() == "true"

# 默认配置
DEFAULT_TOTAL_THOUGHTS = 5
MAX_HISTORY_LENGTH = 1000  # 防止内存溢出
BRANCH_PREFIX = "branch_"
