"""
检查进化触发条件工具
"""
from typing import Dict, Any

from Lib.base.base import tool, ToolRegistry


@tool(
    name="check_evolution_trigger",
    description="Check if current metrics indicate evolution should be triggered. Returns should_evolve and trigger details.",
    schema={
        "type": "object",
        "properties": {},
        "required": []
    }
)
def check_evolution_trigger() -> Dict[str, Any]:
    # 获取状态管理器
    from Lib.evolution.evolve_core import get_state_manager
    state_mgr = get_state_manager()

    trigger = state_mgr.metrics.check_evolution_triggers()
    stats = state_mgr.metrics.get_stats()

    return {
        "should_evolve": trigger is not None,
        "trigger_event": {
            "trigger_type": trigger["trigger_type"],
            "metrics_snapshot": trigger.get("metrics_snapshot", {})
        } if trigger else None,
        "current_metrics": stats.get("current_metrics", {}),
        "thresholds": stats.get("thresholds", {})
    }
