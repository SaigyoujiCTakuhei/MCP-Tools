"""
评估变体适应度工具
"""
from typing import Dict, Any

from Lib.base import tool, ToolRegistry


@tool(
    name="evaluate_variant",
    description="Evaluate fitness of a variant based on test results. Returns fitness score.",
    schema={
        "type": "object",
        "properties": {
            "variant_id": {"type": "string", "description": "UUID of the variant"},
            "test_results": {"type": "object", "properties": {
                "success_rate": {"type": "number"},
                "avg_response_time": {"type": "number"},
                "error_count": {"type": "integer", "default": 0},
                "resource_usage": {"type": "object", "default": {}}
            }, "required": ["success_rate", "avg_response_time"]}
        },
        "required": ["variant_id", "test_results"]
    }
)
def evaluate_variant(
    variant_id: str,
    test_results: Dict[str, Any]
) -> Dict[str, Any]:
    # 获取状态管理器
    from Lib.evolve_core import get_state_manager, TestResults
    state_mgr = get_state_manager()

    variant = state_mgr.get_variant_by_id(variant_id)
    if variant is None:
        return {"error": f"Variant {variant_id} not found"}

    results = TestResults(
        variant_id=variant.id,
        success_rate=float(test_results.get("success_rate", 0)),
        avg_response_time=float(test_results.get("avg_response_time", 0)),
        error_count=int(test_results.get("error_count", 0)),
        resource_usage=dict(test_results.get("resource_usage", {}))
    )

    fitness = state_mgr.evaluator.evaluate(variant, results)

    return {
        "variant_id": variant_id,
        "fitness_score": fitness
    }
