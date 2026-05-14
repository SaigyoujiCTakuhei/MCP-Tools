"""
记录指标工具
"""
from typing import Dict, Any, Optional

from Lib.base import tool, ToolRegistry


@tool(
    name="record_metrics",
    description="Record metrics for a task execution. Returns success status and data point count.",
    schema={
        "type": "object",
        "properties": {
            "task_id": {"type": "string", "description": "Unique task identifier"},
            "response_time": {"type": "number", "description": "Response time in seconds"},
            "success": {"type": "boolean", "description": "Whether task succeeded"},
            "token_usage": {"type": "integer", "default": 0, "description": "Tokens consumed"},
            "error_type": {"type": "string", "default": None, "description": "Type of error if failed"},
            "agent_id": {"type": "string", "default": None, "description": "Agent identifier"}
        },
        "required": ["task_id", "response_time", "success"]
    }
)
def record_metrics(
    task_id: str,
    response_time: float,
    success: bool,
    token_usage: int = 0,
    error_type: Optional[str] = None,
    agent_id: Optional[str] = None
) -> Dict[str, Any]:
    # 获取状态管理器
    from Lib.evolve_core import get_state_manager
    state_mgr = get_state_manager()

    state_mgr.metrics.collect(
        task_id=task_id,
        metrics={
            "response_time": response_time,
            "success": success,
            "token_usage": token_usage,
            "error_type": error_type
        },
        agent_id=agent_id
    )

    return {
        "success": True,
        "task_id": task_id,
        "data_points_stored": len(state_mgr.metrics.data_points)
    }
