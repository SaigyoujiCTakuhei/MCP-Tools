"""
检测异常工具
"""
from typing import Dict, Any, Optional

from Lib.base import tool, ToolRegistry


@tool(
    name="detect_anomalies",
    description="Detect anomalies in metrics data. Returns list of detected anomalies.",
    schema={
        "type": "object",
        "properties": {
            "sensitivity": {"type": "number", "default": 2.0, "description": "Z-score threshold (1.0-5.0)"},
            "window_minutes": {"type": "integer", "default": None, "description": "Time window in minutes"}
        },
        "required": []
    }
)
def detect_anomalies(
    sensitivity: float = 2.0,
    window_minutes: Optional[int] = None
) -> Dict[str, Any]:
    # 获取状态管理器
    from Lib.evolve_core import get_state_manager
    state_mgr = get_state_manager()

    anomalies = state_mgr.metrics.detect_anomalies(
        sensitivity=sensitivity,
        window_minutes=window_minutes
    )

    return {
        "sensitivity": sensitivity,
        "anomaly_count": len(anomalies),
        "anomalies": [
            {
                "metric": a.metric_name,
                "value": a.value,
                "expected_range": a.expected_range,
                "severity": a.severity,
                "timestamp": a.timestamp.isoformat()
            }
            for a in anomalies
        ]
    }
