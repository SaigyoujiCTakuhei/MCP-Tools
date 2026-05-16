"""
核心状态机逻辑
【猫娘修改】：迁移原 TypeScript lib.ts 的 SequentialThinkingServer 类。
采用线程局部存储隔离会话状态，支持线性推进、分支探索与自我修正。
"""
import json
import logging
import threading
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

from .config import DISABLE_THOUGHT_LOGGING, DEFAULT_TOTAL_THOUGHTS, MAX_HISTORY_LENGTH

# 日志配置（替代原 ts 的 chalk）
logger = logging.getLogger("sequential_thinking")


@dataclass
class ThoughtData:
    """思考步骤数据模型"""
    thought: str
    thoughtNumber: int
    totalThoughts: int
    isRevision: bool = False
    revisesThought: Optional[int] = None
    branchFromThought: Optional[int] = None
    branchId: Optional[str] = None
    needsMoreThoughts: bool = False
    nextThoughtNeeded: bool = True


class ThoughtState:
    """单线程/单会话的思考状态管理器"""
    def __init__(self):
        self.thoughtHistory: List[ThoughtData] = []
        self.branches: Dict[str, List[ThoughtData]] = {}
        self._lock = threading.Lock()

    def add_thought(self, data: ThoughtData) -> None:
        with self._lock:
            # 动态调整总数（若当前编号超过预估）
            if data.thoughtNumber > data.totalThoughts:
                data.totalThoughts = data.thoughtNumber
            
            self.thoughtHistory.append(data)
            
            # 分支记录
            if data.branchFromThought is not None and data.branchId is not None:
                if data.branchId not in self.branches:
                    self.branches[data.branchId] = []
                self.branches[data.branchId].append(data)

    def get_snapshot(self, next_needed: bool) -> Dict[str, Any]:
        with self._lock:
            return {
                "thoughtNumber": self.thoughtHistory[-1].thoughtNumber if self.thoughtHistory else 0,
                "totalThoughts": self.thoughtHistory[-1].totalThoughts if self.thoughtHistory else 0,
                "nextThoughtNeeded": next_needed,
                "branches": list(self.branches.keys()),
                "thoughtHistoryLength": len(self.thoughtHistory)
            }


# 线程局部存储，确保多客户端并发隔离
_thread_local = threading.local()


def get_current_state() -> ThoughtState:
    """获取或初始化当前线程的思考状态"""
    if not hasattr(_thread_local, "state"):
        _thread_local.state = ThoughtState()
    return _thread_local.state


def process_thought(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理单次思考步骤调用
    【猫娘修改】：对齐原 ts processThought 逻辑，返回标准 MCP 格式响应
    """
    try:
        # 参数校验与默认值处理
        thought = input_data.get("thought", "")
        thought_number = int(input_data.get("thoughtNumber", 1))
        total_thoughts = int(input_data.get("totalThoughts", DEFAULT_TOTAL_THOUGHTS))
        next_needed = bool(input_data.get("nextThoughtNeeded", True))
        is_revision = bool(input_data.get("isRevision", False))
        revises_thought = input_data.get("revisesThought")
        branch_from = input_data.get("branchFromThought")
        branch_id = input_data.get("branchId")
        needs_more = bool(input_data.get("needsMoreThoughts", False))

        state = get_current_state()
        data = ThoughtData(
            thought=thought,
            thoughtNumber=thought_number,
            totalThoughts=total_thoughts,
            isRevision=is_revision,
            revisesThought=revises_thought,
            branchFromThought=branch_from,
            branchId=branch_id,
            needsMoreThoughts=needs_more,
            nextThoughtNeeded=next_needed
        )

        # 记录到状态机
        state.add_thought(data)

        # 终端日志输出（替代 chalk 渲染）
        if not DISABLE_THOUGHT_LOGGING:
            _format_and_log(data)

        # 返回结构化快照
        snapshot = state.get_snapshot(next_needed)
        return {
            "content": [{"type": "text", "text": json.dumps(snapshot, ensure_ascii=False, indent=2)}],
            "structuredContent": snapshot
        }

    except Exception as e:
        logger.error(f"Thought processing failed: {e}", exc_info=True)
        return {
            "content": [{"type": "text", "text": json.dumps({"error": str(e), "status": "failed"}, ensure_ascii=False)}],
            "structuredContent": {"error": str(e), "status": "failed"},
            "isError": True
        }


def _format_and_log(data: ThoughtData) -> None:
    """格式化并打印思考步骤（替代原 ts 的 formatThought + console.error）"""
    prefix_map = {
        True: "[🔄 Revision]",
        data.branchFromThought is not None: f"[🌿 Branch#{data.branchId}]",
        False: "[💭 Thought]"
    }
    prefix = next((v for k, v in prefix_map.items() if k), "[💭 Thought]")
    context = ""
    if data.isRevision and data.revisesThought:
        context = f" (revising thought {data.revisesThought})"
    elif data.branchFromThought:
        context = f" (from thought {data.branchFromThought}, ID: {data.branchId})"

    header = f"{prefix} {data.thoughtNumber}/{data.totalThoughts}{context}"
    border_len = max(len(header), len(data.thought)) + 4
    border = "─" * border_len
    
    log_msg = f"\n┌{'─' * border_len}┐\n│ {header} │\n├{'─' * border_len}┤\n│ {data.thought.ljust(border_len - 2)} │\n└{'─' * border_len}┘"
    logger.info(log_msg)
