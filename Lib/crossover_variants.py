"""
变体交叉工具
"""
from typing import Dict, Any

from Lib.base import tool, ToolRegistry


@tool(
    name="crossover_variants",
    description="Combine two variants to create offspring. Returns offspring list.",
    schema={
        "type": "object",
        "properties": {
            "parent1_id": {"type": "string", "description": "UUID of first parent"},
            "parent2_id": {"type": "string", "description": "UUID of second parent"}
        },
        "required": ["parent1_id", "parent2_id"]
    }
)
def crossover_variants(
    parent1_id: str,
    parent2_id: str
) -> Dict[str, Any]:
    # 获取状态管理器
    from Lib.evolve_core import get_state_manager
    from Lib.evolve_core import Variant
    state_mgr = get_state_manager()

    parent1 = state_mgr.get_variant_by_id(parent1_id)
    parent2 = state_mgr.get_variant_by_id(parent2_id)

    if parent1 is None:
        return {"error": f"Parent variant {parent1_id} not found"}
    if parent2 is None:
        return {"error": f"Parent variant {parent2_id} not found"}

    offspring1, offspring2 = state_mgr.generator.crossover(parent1, parent2)
    state_mgr.store_variants([offspring1, offspring2])

    return {
        "parent1_id": parent1_id,
        "parent2_id": parent2_id,
        "offspring": [
            {"id": str(offspring1.id), "prompt_preview": offspring1.prompt[:100]},
            {"id": str(offspring2.id), "prompt_preview": offspring2.prompt[:100]}
        ]
    }
