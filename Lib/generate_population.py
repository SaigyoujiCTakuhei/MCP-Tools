"""
生成种群工具
"""
from typing import Dict, Any, Optional
from uuid import UUID

from Lib.base import tool, ToolRegistry


@tool(
    name="generate_population",
    description="Generate a population of prompt variants for evolution. Returns variants list and stats.",
    schema={
        "type": "object",
        "properties": {
            "base_prompt": {"type": "string", "description": "Starting prompt to mutate"},
            "size": {"type": "integer", "default": 50, "description": "Number of variants (1-1000)"},
            "seed": {"type": "integer", "default": None, "description": "Random seed for reproducibility"}
        },
        "required": ["base_prompt"]
    }
)
def generate_population(
    base_prompt: str,
    size: int = 50,
    seed: Optional[int] = None
) -> Dict[str, Any]:
    # 获取状态管理器
    from Lib.evolve_core import get_state_manager
    state_mgr = get_state_manager()

    if seed is not None:
        state_mgr.generator.set_random_seed(seed)

    size = min(size, 1000)  # 限制最大数量
    variants = state_mgr.generator.generate_population(base_prompt, size)
    state_mgr.store_variants(variants)

    return {
        "count": len(variants),
        "variants": [
            {"id": str(v.id), "prompt_preview": v.prompt[:100], "generation": v.generation}
            for v in variants[:100]  # 限制返回数量
        ],
        "seed": seed
    }
