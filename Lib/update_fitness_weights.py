"""
更新适应度权重工具
"""
from typing import Dict, Any

from Lib.base import tool, ToolRegistry


@tool(
    name="update_fitness_weights",
    description="Update weights for fitness functions. Returns updated weights.",
    schema={
        "type": "object",
        "properties": {
            "weights": {"type": "object", "description": "Map of function names to new weights",
                       "properties": {
                           "speed": {"type": "number"},
                           "accuracy": {"type": "number"},
                           "efficiency": {"type": "number"}
                       }}
        },
        "required": ["weights"]
    }
)
def update_fitness_weights(weights: Dict[str, float]) -> Dict[str, Any]:
    # 获取状态管理器
    from Lib.evolve_core import get_state_manager
    state_mgr = get_state_manager()

    state_mgr.evaluator.update_weights(weights)

    return {
        "success": True,
        "updated_weights": weights,
        "registered_functions": state_mgr.evaluator.get_registered_functions()
    }
