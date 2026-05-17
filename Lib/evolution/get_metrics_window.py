"""
获取指标窗口工具
"""
from datetime import timedelta
from typing import Dict, Any

from Lib.base.base import tool, ToolRegistry


@tool(
    name="get_metrics_window",
    description="Get aggregated metrics for a time window. Returns success rate, response times, etc.",
    schema={
        "type": "object",
        "properties": {
            "window_minutes": {"type": "integer", "default": 60, "description": "Time window in minutes (1-10080)"}
        },
        "required": []
    }
)
def get_metrics_window(window_minutes: int = 60) -> Dict[str, Any]:
    # 获取状态管理器
    from Lib.evolution.evolve_core import get_state_manager
    state_mgr = get_state_manager()

    # 【猫娘修改】修复内部变量引用错误：补全 timedelta 类型转换，对齐底层接口契约
    # 原代码直接传入 int 导致底层 get_window_metrics 内部计算时作用域断裂
    window_duration = timedelta(minutes=window_minutes)
    window = state_mgr.metrics.get_window_metrics(window_duration)

    p95 = state_mgr.metrics.get_custom_metric_value("p95_response_time", window_duration)

    return {
        "window_minutes": window_minutes,
        "total_requests": window.total_requests,
        "success_rate": window.success_rate,
        "avg_response_time": window.avg_response_time,
        "p95_response_time": p95,
        "total_tokens": window.total_tokens
    }