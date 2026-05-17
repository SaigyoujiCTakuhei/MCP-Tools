"""
开始进化周期工具
（猫娘修改：被动式手动触发 + 自动流水线执行一代）
"""
import asyncio
import json
from datetime import datetime
from typing import Any, Dict, Optional

from Lib.base.base import tool, ToolRegistry


@tool(
    name="start_evolution",
    description="Start a new evolution cycle to improve agent performance. Returns cycle_id, status, and config. (猫娘修改：触发后自动执行一代流水线)",
    schema={
        "type": "object",
        "properties": {
            "trigger_type": {"type": "string", "default": "manual"},
            "metrics_snapshot": {"type": "object", "default": None},
            "config_overrides": {"type": "object", "default": None}
        },
        "required": []
    }
)
def start_evolution(
    trigger_type: str = "manual",
    metrics_snapshot: Optional[Dict[str, float]] = None,
    config_overrides: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    # 获取状态管理器
    from Lib.evolution.evolve_core import get_state_manager
    from uuid import UUID
    
    state_mgr = get_state_manager()

    # 开始周期
    cycle_id = state_mgr.start_cycle(trigger_type, config_overrides)

    # 【猫娘修改】被动式手动触发后，自动执行一代流水线
    pipeline_config = {
        "base_prompt": "Default evolution prompt",
        "population_size": state_mgr.cycles[cycle_id]["config"]["population_size"]
    }
    
    # 【猫娘修改】调用自动流水线执行一代
    generation_result = {"error": "Pipeline not executed"}
    try:
        generation_result = state_mgr.pipeline.run_generation(cycle_id, pipeline_config)
    except Exception as e:
        generation_result = {
            "cycle_id": cycle_id,
            "generation": 0,
            "error": str(e)
        }

    # 【猫娘修复】构建返回结果，确保所有字段都是基本类型
    result = {
        "cycle_id": str(cycle_id),
        "status": "running",
        "config": {
            "population_size": int(state_mgr.cycles[cycle_id]["config"]["population_size"]),
            "max_generations": int(state_mgr.cycles[cycle_id]["config"]["max_generations"]),
            "fitness_threshold": float(state_mgr.cycles[cycle_id]["config"]["fitness_threshold"])
        },
        "started_at": datetime.now().isoformat(),
        "first_generation": {
            "cycle_id": str(generation_result.get("cycle_id", cycle_id)),
            "generation": int(generation_result.get("generation", 0)),
            "population_size": int(generation_result.get("population_size", 0)),
            "best_fitness": float(generation_result.get("best_fitness", 0)) if generation_result.get("best_fitness") is not None else 0,
            "avg_fitness": float(generation_result.get("avg_fitness", 0)) if generation_result.get("avg_fitness") is not None else 0
        }
    }
    
    return result