"""
检查文本安全工具
"""
from typing import Dict, Any

from Lib.base import tool, ToolRegistry


@tool(
    name="check_safety",
    description="Run safety validation on text/prompt. Returns is_safe and violations.",
    schema={
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Text to validate"},
            "include_policy": {"type": "boolean", "default": True, "description": "Whether to check against default policy"}
        },
        "required": ["text"]
    }
)
def check_safety(
    text: str,
    include_policy: bool = True
) -> Dict[str, Any]:
    # 获取状态管理器
    from Lib.evolve_core import get_state_manager, SafetyPolicy
    state_mgr = get_state_manager()

    policy = SafetyPolicy() if include_policy else None
    result = state_mgr.validator.check_safety(text, policy)

    return {
        "is_safe": result.is_safe,
        "violations": [{"rule_name": v.rule_name, "severity": v.severity, "description": v.description} for v in result.violations],
        "warnings": result.warnings
    }
