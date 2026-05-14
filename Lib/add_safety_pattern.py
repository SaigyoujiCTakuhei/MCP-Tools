"""
添加安全模式工具
"""
from typing import Dict, Any

from Lib.base import tool, ToolRegistry


@tool(
    name="add_safety_pattern",
    description="Add a custom safety pattern. Returns success status.",
    schema={
        "type": "object",
        "properties": {
            "category": {"type": "string", "description": "Pattern category (e.g., 'prompt_injection')"},
            "pattern": {"type": "string", "description": "Regex pattern string"}
        },
        "required": ["category", "pattern"]
    }
)
def add_safety_pattern(
    category: str,
    pattern: str
) -> Dict[str, Any]:
    # 获取状态管理器
    from Lib.evolve_core import get_state_manager
    state_mgr = get_state_manager()

    state_mgr.validator.add_pattern(category, pattern)

    return {
        "success": True,
        "category": category,
        "pattern": pattern
    }
