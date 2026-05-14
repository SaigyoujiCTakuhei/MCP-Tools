"""
验证变体安全工具
"""
from typing import Dict, Any, Optional

from Lib.base import tool, ToolRegistry


@tool(
    name="validate_variant",
    description="Run full safety validation on a variant. Returns is_valid and violations.",
    schema={
        "type": "object",
        "properties": {
            "variant_id": {"type": "string", "description": "UUID of variant to validate"},
            "policy": {"type": "object", "default": None, "description": "Optional custom safety policy"}
        },
        "required": ["variant_id"]
    }
)
def validate_variant(
    variant_id: str,
    policy: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    # 获取状态管理器
    from Lib.evolve_core import get_state_manager, SafetyPolicy
    state_mgr = get_state_manager()

    variant = state_mgr.get_variant_by_id(variant_id)
    if variant is None:
        return {"error": f"Variant {variant_id} not found"}

    # 创建策略
    safety_policy = SafetyPolicy()
    if policy:
        safety_policy.forbidden_patterns = policy.get("forbidden_patterns", safety_policy.forbidden_patterns)

    result = state_mgr.validator.validate_variant(variant, safety_policy)

    return {
        "variant_id": variant_id,
        "is_valid": result.is_safe,
        "errors": [v.description for v in result.violations]
    }
