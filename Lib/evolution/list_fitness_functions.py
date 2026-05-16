"""
列出适应度函数工具
"""
from typing import Dict, Any

from Lib.base.base import tool, ToolRegistry


@tool(
    name="list_fitness_functions",
    description="List all registered fitness functions. Returns functions list.",
    schema={
        "type": "object",
        "properties": {},
        "required": []
    }
)
def list_fitness_functions() -> Dict[str, Any]:
    # 获取状态管理器
    from Lib.evolution.evolve_core import get_state_manager
    state_mgr = get_state_manager()

    functions = state_mgr.evaluator.get_registered_functions()

    return {
        "count": len(functions),
        "functions": functions
    }
