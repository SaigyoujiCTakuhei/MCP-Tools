"""
变异 Prompt 工具
"""
from typing import Dict, Any

from Lib.base import tool, ToolRegistry


@tool(
    name="mutate_prompt",
    description="Apply a specific mutation to a prompt. Returns mutated prompt and complexity metrics.",
    schema={
        "type": "object",
        "properties": {
            "prompt": {"type": "string", "description": "Original prompt text"},
            "mutation_type": {"type": "string", "default": "paraphrase", "description": "Type: paraphrase, instruction_add, context_expand, cot_injection, tone_shift"}
        },
        "required": ["prompt"]
    }
)
def mutate_prompt(
    prompt: str,
    mutation_type: str = "paraphrase"
) -> Dict[str, Any]:
    # 验证变异类型
    valid_types = ["paraphrase", "instruction_add", "context_expand", "cot_injection", "tone_shift"]
    if mutation_type not in valid_types:
        return {"error": f"Invalid mutation type. Must be one of: {valid_types}"}

    # 获取状态管理器
    from Lib.evolve_core import get_state_manager
    state_mgr = get_state_manager()

    mutated = state_mgr.generator.mutate_prompt(prompt, mutation_type)
    complexity = state_mgr.generator.analyze_prompt_complexity(mutated)

    return {
        "original_prompt": prompt,
        "mutated_prompt": mutated,
        "mutation_type": mutation_type,
        "complexity_metrics": {
            "sentence_count": complexity.sentence_count,
            "word_count": complexity.word_count,
            "avg_sentence_length": complexity.avg_sentence_length,
            "lexical_diversity": complexity.lexical_diversity,
            "instruction_density": complexity.instruction_density,
            "complexity_score": complexity.complexity_score
        }
    }
