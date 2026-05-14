"""
注册适应度函数工具
"""
from typing import Dict, Any, Optional

from Lib.base import tool, ToolRegistry


@tool(
    name="register_fitness_function",
    description="Register a predefined fitness function. Returns success status.",
    schema={
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Name of function (speed, accuracy, efficiency)"},
            "weight": {"type": "number", "default": 1.0, "description": "Weight in weighted sum (0-10)"},
            "description": {"type": "string", "default": None, "description": "Human-readable description"}
        },
        "required": ["name"]
    }
)
def register_fitness_function(
    name: str,
    weight: float = 1.0,
    description: Optional[str] = None
) -> Dict[str, Any]:
    # 获取状态管理器
    from Lib.evolve_core import get_state_manager
    state_mgr = get_state_manager()

    predefined = ["speed", "accuracy", "efficiency"]

    if name not in predefined:
        return {
            "error": "Only predefined functions supported for safety",
            "available": predefined
        }

    # 更新权重
    state_mgr.evaluator.update_weights({name: weight})

    return {
        "success": True,
        "name": name,
        "weight": weight,
        "description": description,
        "registered_functions": state_mgr.evaluator.get_registered_functions()
    }
