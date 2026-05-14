"""
生成 A/B 测试对工具
"""
from typing import Dict, Any

from Lib.base import tool, ToolRegistry


@tool(
    name="generate_ab_pair",
    description="Create an A/B test pair from a base variant. Returns variant_a and variant_b.",
    schema={
        "type": "object",
        "properties": {
            "base_variant_id": {"type": "string", "description": "UUID of the base variant"}
        },
        "required": ["base_variant_id"]
    }
)
def generate_ab_pair(base_variant_id: str) -> Dict[str, Any]:
    # 获取状态管理器
    from Lib.evolve_core import get_state_manager
    state_mgr = get_state_manager()

    base_variant = state_mgr.get_variant_by_id(base_variant_id)
    if base_variant is None:
        return {"error": f"Base variant {base_variant_id} not found"}

    # 保守变异（Variant A）
    from Lib.evolve_core import PromptMutationType
    prompt_a = state_mgr.generator.mutate_prompt(base_variant.prompt, PromptMutationType.PARAPHRASE)
    prompt_a = state_mgr.generator.mutate_prompt(prompt_a, PromptMutationType.INSTRUCTION_ADD)
    config_a = base_variant.configuration.copy()
    if "temperature" in config_a:
        config_a["temperature"] = max(0.1, config_a["temperature"] - 0.1)

    variant_a = type(base_variant)(
        id=None, parent_ids=[base_variant.id], generation=base_variant.generation + 1,
        prompt=prompt_a, configuration=config_a
    )

    # 激进变异（Variant B）
    prompt_b = state_mgr.generator.mutate_prompt(base_variant.prompt, PromptMutationType.CONTEXT_EXPAND)
    prompt_b = state_mgr.generator.mutate_prompt(prompt_b, PromptMutationType.COT_INJECTION)
    prompt_b = state_mgr.generator.mutate_prompt(prompt_b, PromptMutationType.TONE_SHIFT)
    config_b = base_variant.configuration.copy()
    if "temperature" in config_b:
        config_b["temperature"] = min(1.5, config_b["temperature"] + 0.2)

    variant_b = type(base_variant)(
        id=None, parent_ids=[base_variant.id], generation=base_variant.generation + 1,
        prompt=prompt_b, configuration=config_b
    )

    # 重新生成 UUID（因为构造函数没有传入）
    from uuid import uuid4
    variant_a.id = uuid4()
    variant_b.id = uuid4()

    state_mgr.store_variants([variant_a, variant_b])

    return {
        "base_variant_id": base_variant_id,
        "variant_a": {"id": str(variant_a.id), "prompt_preview": variant_a.prompt[:100]},
        "variant_b": {"id": str(variant_b.id), "prompt_preview": variant_b.prompt[:100]}
    }
