"""
获取指标窗口工具
"""
from typing import Dict, Any

from Lib.base import tool, ToolRegistry


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
    from Lib.evolve_core import get_state_manager
    state_mgr = get_state_manager()

    window = state_mgr.metrics.get_window_metrics(window_minutes)

    p95 = state_mgr.metrics.get_custom_metric_value("p95_response_time", window_minutes)

    return {
        "window_minutes": window_minutes,
        "total_requests": window.total_requests,
        "success_rate": window.success_rate,
        "avg_response_time": window.avg_response_time,
        "p95_response_time": p95,
        "total_tokens": window.total_tokens
    }
