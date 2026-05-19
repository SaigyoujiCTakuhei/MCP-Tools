"""
工具注册装饰器入口
【猫娘修改】：对齐原 ts index.ts，使用 base.py 的 @tool 装饰器注册 sequentialthinking。
包含显式 JSON Schema 定义与输入预处理逻辑。
"""
import json
from typing import Any, Dict

from Lib.base.base import tool

# 显式 Schema 定义（替代原 ts 的 Zod 运行时校验，由 MCP 框架层处理）
SEQUENTIAL_THINKING_SCHEMA = {
    "type": "object",
    "properties": {
        "thought": {"type": "string", "description": "Your current thinking step"},
        "nextThoughtNeeded": {"type": "boolean", "description": "Whether another thought step is needed"},
        "thoughtNumber": {"type": "integer", "minimum": 1, "description": "Current thought number (numeric value, e.g., 1, 2, 3)"},
        "totalThoughts": {"type": "integer", "minimum": 1, "description": "Estimated total thoughts needed (numeric value, e.g., 5, 10)"},
        "isRevision": {"type": "boolean", "description": "Whether this revises previous thinking"},
        "revisesThought": {"type": "integer", "minimum": 1, "description": "Which thought is being reconsidered"},
        "branchFromThought": {"type": "integer", "minimum": 1, "description": "Branching point thought number"},
        "branchId": {"type": "string", "description": "Branch identifier"},
        "needsMoreThoughts": {"type": "boolean", "description": "If more thoughts are needed"}
    },
    "required": ["thought", "nextThoughtNeeded", "thoughtNumber", "totalThoughts"]
}

# MCP 工具元数据标注（对齐原 ts annotations）
TOOL_ANNOTATIONS = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False
}


@tool(
    name="sequentialthinking",
    description="""A detailed tool for dynamic and reflective problem-solving through thoughts.
This tool helps analyze problems through a flexible thinking process that can adapt and evolve.
Each thought can build on, question, or revise previous insights as understanding deepens.

When to use this tool:
- Breaking down complex problems into steps
- Planning and design with room for revision
- Analysis that might need course correction
- Problems where the full scope might not be clear initially
- Problems that require a multi-step solution
- Tasks that need to maintain context over multiple steps
- Situations where irrelevant information needs to be filtered out

Key features:
- You can adjust total_thoughts up or down as you progress
- You can question or revise previous thoughts
- You can add more thoughts even after reaching what seemed like the end
- You can express uncertainty and explore alternative approaches
- Not every thought needs to build linearly - you can branch or backtrack
- Generates a solution hypothesis
- Verifies the hypothesis based on the Chain of Thought steps
- Repeats the process until satisfied
- Provides a correct answer

Parameters explained:
- thought: Your current thinking step, which can include:
  * Regular analytical steps
  * Revisions of previous thoughts
  * Questions about previous decisions
  * Realizations about needing more analysis
  * Changes in approach
  * Hypothesis generation
  * Hypothesis verification
- nextThoughtNeeded: True if you need more thinking, even if at what seemed like the end
- thoughtNumber: Current number in sequence (can go beyond initial total if needed)
- totalThoughts: Current estimate of thoughts needed (can be adjusted up/down)
- isRevision: A boolean indicating if this thought revises previous thinking
- revisesThought: If is_revision is true, which thought number is being reconsidered
- branchFromThought: If branching, which thought number is the branching point
- branchId: Identifier for the current branch (if any)
- needsMoreThoughts: If reaching end but realizing more thoughts needed

You should:
1. Start with an initial estimate of needed thoughts, but be ready to adjust
2. Feel free to question or revise previous thoughts
3. Don't hesitate to add more thoughts if needed, even at the "end"
4. Express uncertainty when present
5. Mark thoughts that revise previous thinking or branch into new paths
6. Ignore information that is irrelevant to the current step
7. Generate a solution hypothesis when appropriate
8. Verify the hypothesis based on the Chain of Thought steps
9. Repeat the process until satisfied with the solution
10. Provide a single, ideally correct answer as the final output
11. Only set nextThoughtNeeded to false when truly done and a satisfactory answer is reached""",
    schema=SEQUENTIAL_THINKING_SCHEMA
)
def sequentialthinking(
    thought: str,
    nextThoughtNeeded: bool,
    thoughtNumber: int,
    totalThoughts: int,
    isRevision: bool = False,
    revisesThought: int = None,
    branchFromThought: int = None,
    branchId: str = None,
    needsMoreThoughts: bool = False
) -> Dict[str, Any]:
    """
    Sequential Thinking MCP Tool Entry Point
    【猫娘修改】：输入预处理 -> 委托 core -> 标准 MCP 响应格式化
    """
    # 输入预处理（对齐原 ts 的 coercedBoolean 逻辑）
    def safe_bool(val):
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            return val.lower() == "true"
        return False

    def safe_int(val, default=1):
        try:
            return max(1, int(val))
        except (ValueError, TypeError):
            return default

    payload = {
        "thought": str(thought),
        "nextThoughtNeeded": safe_bool(nextThoughtNeeded),
        "thoughtNumber": safe_int(thoughtNumber),
        "totalThoughts": safe_int(totalThoughts),
        "isRevision": safe_bool(isRevision),
        "revisesThought": safe_int(revisesThought) if revisesThought is not None else None,
        "branchFromThought": safe_int(branchFromThought) if branchFromThought is not None else None,
        "branchId": str(branchId) if branchId is not None else None,
        "needsMoreThoughts": safe_bool(needsMoreThoughts)
    }

    # 委托核心处理函数
    result = __import__('Lib.sequential_thinking.thinking_core', fromlist=['process_thought']).process_thought(payload)

    # 标准 MCP 响应结构（对齐原 ts 的 structuredContent 返回）
    return {
        "content": result.get("content", []),
        "structuredContent": result.get("structuredContent", {}),
        "isError": result.get("isError", False)
    }
