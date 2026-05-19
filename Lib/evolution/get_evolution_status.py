"""
获取进化状态工具（适配周期上下文与存在性校验）
（猫娘修改：适配索引策略，懒加载完整 Variant 对象）
"""
from datetime import datetime
from typing import Optional, Dict, Any
from Lib.base.base import tool, ToolRegistry
from Lib.evolution.evolve_core import get_state_manager

@tool(
    name="get_evolution_status",
    description="Get status of an evolution cycle. Returns status, generation, fitness scores, and progress. (猫娘修改：适配索引策略)",
    schema={
        "type": "object",
        "properties": {
            "cycle_id": {"type": "string", "default": None}
        },
        "required": []
    }
)
def get_evolution_status(cycle_id: Optional[str] = None) -> Dict[str, Any]:
    state_mgr = get_state_manager()

    # 【猫娘修改】修复参数传递引号 Bug：清理 cycle_id 中可能存在的多余引号字符
    # 当 MCP 框架传递带引号的字符串时（如 "\"cycle_xxx\""），需要去除首尾引号
    if cycle_id is not None:
        cycle_id = cycle_id.strip()
        # 去除首尾的双引号或单引号
        if len(cycle_id) >= 2 and ((cycle_id[0] == '"' and cycle_id[-1] == '"') or (cycle_id[0] == "'" and cycle_id[-1] == "'")):
            cycle_id = cycle_id[1:-1]
            # 递归清理（防止多层引号）
            cycle_id = cycle_id.strip()

    # 【猫娘修改】修复空参数解析异常：拦截清理后的空字符串，防止穿透至底层拼接逻辑
    if not cycle_id:
        return {"status": "no_active_cycle", "message": "Cycle ID is empty or not provided"}

    # 【状态同步修复】优先使用传入 ID，无参时自动同步获取当前周期
    if cycle_id is None:
        cycle_id = state_mgr.get_current_cycle_id()

    if cycle_id is None:
        return {"status": "no_active_cycle", "message": "No evolution cycles have been started"}

    # 【增加存在性校验】安全获取周期数据
    cycle = state_mgr._ensure_cycle_exists(cycle_id)
    if cycle is None:
        return {"error": f"Cycle {cycle_id} not found"}

    # 【引入周期上下文】从隔离上下文中获取真实种群与适应度数据
    ctx = state_mgr.get_cycle_context(cycle_id)
    
    # 【猫娘修改】适配索引策略：索引中已包含 fitness_score，无需懒加载
    variants_index = ctx.get("variants", {}) if ctx else {}
    fitness_scores = [v.get("fitness_score") for v in variants_index.values() if v.get("fitness_score") is not None]

    return {
        "cycle_id": cycle_id,
        "status": cycle["status"],
        "generation": cycle["current_generation"],
        "population_size": len(variants_index),  # 【猫娘修改】基于索引计算真实种群数
        "best_fitness": max(fitness_scores) if fitness_scores else None,
        "avg_fitness": sum(fitness_scores) / len(fitness_scores) if fitness_scores else None,
        "started_at": cycle["started_at"].isoformat() if cycle["started_at"] else None,
        "elapsed_seconds": (datetime.now() - cycle["started_at"]).total_seconds() if cycle["started_at"] else 0,
        "schema_version": 2  # 【猫娘修改】返回当前 Schema 版本
    }