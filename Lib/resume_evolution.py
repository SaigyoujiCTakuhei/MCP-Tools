"""
恢复进化周期工具
（猫娘修改：增加版本检查、索引恢复逻辑）
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

from Lib.base import tool, ToolRegistry


@tool(
    name="resume_evolution",
    description="Resume evolution from a checkpoint. Returns cycle_id and resumed generation. (猫娘修改：适配版本控制与索引策略)",
    schema={
        "type": "object",
        "properties": {
            "checkpoint_path": {"type": "string", "description": "Path to checkpoint file"}
        },
        "required": ["checkpoint_path"]
    }
)
def resume_evolution(checkpoint_path: str) -> Dict[str, Any]:
    # 【猫娘修复】Issue 13: 实现基础检查点恢复功能
    try:
        if not os.path.exists(checkpoint_path):
            return {"error": f"Checkpoint file not found: {checkpoint_path}"}
        
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            checkpoint_data = json.load(f)
        
        # 【猫娘修改】增加版本检查：检查 checkpoint 的 schema_version
        checkpoint_version = checkpoint_data.get("schema_version", 1)
        if checkpoint_version not in [1, 2]:
            return {"error": f"Unsupported checkpoint schema version: {checkpoint_version}"}
        
        # 获取状态管理器
        from Lib.evolve_core import get_state_manager
        state_mgr = get_state_manager()
        
        # 恢复配置
        config_overrides = checkpoint_data.get("config", {})
        trigger_type = checkpoint_data.get("trigger_type", "manual")
        
        # 开始新周期并注入历史数据
        cycle_id = state_mgr.start_cycle(trigger_type, config_overrides)
        
        # 【猫娘修改】恢复变体索引（仅恢复轻量元数据）
        if "variants" in checkpoint_data:
            # 【猫娘修改】将 checkpoint 中的完整 Variant 转换为索引存储
            for v_dict in checkpoint_data["variants"]:
                from Lib.evolve_core import Variant
                variant = Variant(
                    id=v_dict["id"],
                    parent_ids=[x for x in v_dict.get("parent_ids", [])],
                    generation=v_dict.get("generation", 0),
                    prompt=v_dict.get("prompt", ""),
                    configuration=v_dict.get("configuration", {"temperature": 0.7}),
                    created_at=datetime.fromisoformat(v_dict["created_at"]),
                    fitness_score=v_dict.get("fitness_score"),
                    is_valid=v_dict.get("is_valid", True)
                )
                state_mgr.store_variants([variant])
        
        if "metrics_data" in checkpoint_data:
            for m in checkpoint_data["metrics_data"]:
                state_mgr.metrics.collect(**m)
                
        return {
            "success": True,
            "cycle_id": cycle_id,
            "resumed_from": checkpoint_path,
            "restored_at": datetime.now().isoformat(),
            "config": config_overrides,
            "checkpoint_version": checkpoint_version,  # 【猫娘修改】返回检查点版本
            "restored_variants": len(checkpoint_data.get("variants", []))  # 【猫娘修改】返回恢复的变体数
        }
    except json.JSONDecodeError as e:
        return {"error": f"Invalid checkpoint format: {e}"}
    except Exception as e:
        return {"error": f"Failed to resume: {e}"}