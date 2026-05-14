"""
取消进化周期工具
（猫娘修改：适配版本控制，返回版本信息）
"""
from typing import Dict, Any

from Lib.base import tool, ToolRegistry


@tool(
    name="cancel_evolution",
    description="Cancel a running evolution cycle. Returns success status and final state. (猫娘修改：适配版本控制)",
    schema={
        "type": "object",
        "properties": {
            "cycle_id": {"type": "string", "description": "ID of cycle to cancel"}
        },
        "required": ["cycle_id"]
    }
)
def cancel_evolution(cycle_id: str) -> Dict[str, Any]:
    # 获取状态管理器
    from Lib.evolve_core import get_state_manager
    state_mgr = get_state_manager()

    # 【猫娘修复】移除 await，改为同步调用，与 evolve_core.py 中的同步方法保持一致
    success = state_mgr.cancel_cycle(cycle_id)

    if not success:
        return {"error": f"Cycle {cycle_id} not found"}

    cycle = state_mgr.cycles.get(cycle_id)
    return {
        "success": True,
        "cycle_id": cycle_id,
        "final_status": cycle["status"] if cycle else "cancelled",
        "final_generation": cycle["current_generation"] if cycle else 0,
        "schema_version": 2  # 【猫娘修改】返回当前 Schema 版本
    }