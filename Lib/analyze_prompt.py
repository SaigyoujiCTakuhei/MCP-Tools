"""
分析 Prompt 工具
"""
from typing import Dict, Any

from Lib.base import tool, ToolRegistry


@tool(
    name="analyze_prompt",
    description="Analyze prompt complexity and characteristics. Returns complexity metrics.",
    schema={
        "type": "object",
        "properties": {
            "prompt": {"type": "string", "description": "Prompt text to analyze"}
        },
        "required": ["prompt"]
    }
)
def analyze_prompt(prompt: str) -> Dict[str, Any]:
    # 获取状态管理器
    from Lib.evolve_core import get_state_manager
    state_mgr = get_state_manager()

    complexity = state_mgr.generator.analyze_prompt_complexity(prompt)

    return {
        "prompt_length": len(prompt),
        "complexity_metrics": {
            "sentence_count": complexity.sentence_count,
            "word_count": complexity.word_count,
            "avg_sentence_length": complexity.avg_sentence_length,
            "lexical_diversity": complexity.lexical_diversity,
            "instruction_density": complexity.instruction_density,
            "complexity_score": complexity.complexity_score
        }
    }
