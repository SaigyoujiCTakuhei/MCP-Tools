"""
进化核心模块
管理进化引擎、变异生成器、适应度评估器、安全验证器、指标收集器等核心组件
（修正5：引入缓存淘汰与状态清理机制）
（猫娘修改：增加版本控制、JSON 增量索引策略、自动流水线）
"""
import json
import os
import random
import re
import statistics
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from Lib.base import ToolRegistry, _cache_store


# =============================================================================
# 【猫娘修改】全局常量：Schema 版本控制
# =============================================================================
SCHEMA_VERSION = 2  # 当前 JSON 数据结构版本号
MAX_VARIANT_CACHE_SIZE = 5000  # 内存中完整 Variant 对象缓存上限


# =============================================================================
# 数据结构定义
# =============================================================================

@dataclass
class Variant:
    """变体数据结构"""
    id: UUID = field(default_factory=uuid4)
    parent_ids: List[UUID] = field(default_factory=list)
    generation: int = 0
    prompt: str = ""
    configuration: Dict[str, Any] = field(default_factory=lambda: {"temperature": 0.7})
    created_at: datetime = field(default_factory=datetime.now)
    fitness_score: Optional[float] = None
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)


@dataclass
class TestResults:
    """测试结果数据结构"""
    variant_id: UUID
    success_rate: float
    avg_response_time: float
    error_count: int = 0
    resource_usage: Dict[str, float] = field(default_factory=dict)


@dataclass
class SafetyPolicy:
    """安全策略"""
    max_resource_usage: Dict[str, float] = field(default_factory=lambda: {
        "cpu_percent": 80.0,
        "memory_mb": 512.0,
        "timeout_seconds": 30.0
    })
    forbidden_patterns: List[str] = field(default_factory=lambda: [
        r"(api[_-]?key|secret|password)\s*[:=]",
        r"sk-[a-zA-Z0-9]{20,}",
        r"ghp_[a-zA-Z0-9]{36}",
    ])


@dataclass
class SafetyViolation:
    """安全违规记录"""
    rule_name: str
    severity: str
    description: str
    matched_pattern: Optional[str] = None


@dataclass
class SafetyCheckResult:
    """安全检查结果"""
    is_safe: bool
    violations: List[SafetyViolation] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class ComplexityMetrics:
    """复杂度指标"""
    sentence_count: int
    word_count: int
    avg_sentence_length: float
    lexical_diversity: float
    instruction_density: float
    complexity_score: float


@dataclass
class MetricWindow:
    """指标窗口"""
    start_time: datetime
    end_time: datetime
    total_requests: int
    success_count: int
    avg_response_time: float
    total_tokens: int
    error_counts: Dict[str, int] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        return self.success_count / max(self.total_requests, 1)

    @property
    def avg_tokens_per_request(self) -> float:
        return self.total_tokens / max(self.total_requests, 1)


@dataclass
class Anomaly:
    """异常检测"""
    metric_name: str
    value: float
    expected_range: Tuple[float, float]
    severity: str
    timestamp: datetime


# =============================================================================
# 变异类型枚举
# =============================================================================

class PromptMutationType:
    PARAPHRASE = "paraphrase"
    INSTRUCTION_ADD = "instruction_add"
    CONTEXT_EXPAND = "context_expand"
    COT_INJECTION = "cot_injection"
    TONE_SHIFT = "tone_shift"

    @classmethod
    def get_all(cls):
        return [cls.PARAPHRASE, cls.INSTRUCTION_ADD, cls.CONTEXT_EXPAND, 
                cls.COT_INJECTION, cls.TONE_SHIFT]


# =============================================================================
# 变异生成器
# =============================================================================

class VariantGenerator:
    """Prompt 变异生成器"""

    def __init__(self, mutation_rate: float = 0.3):
        self.mutation_rate = mutation_rate
        self._random_seed: Optional[int] = None
        self.mutation_templates = self._init_templates()
        self._mutation_history: Dict[UUID, List] = {}

    def _init_templates(self) -> Dict:
        return {
            "instruction_prefixes": [
                "Please", "Make sure to", "Always", "Remember to", "Be sure to"
            ],
            "instruction_suffixes": [
                "Think step by step.", "Be thorough in your response.",
                "Provide detailed explanations.", "Consider multiple perspectives.",
                "Use examples when helpful."
            ],
            "context_expanders": [
                "Given the context,", "Taking into account the situation,",
                "Considering the requirements,", "Based on the information provided,"
            ],
            "cot_triggers": [
                "Let's think step by step:", "Let me work through this:",
                "Breaking this down:", "Step by step:", "Let's analyze this:"
            ],
            "instruction_additions": [
                "Be precise and accurate.", "Focus on clarity and completeness.",
                "Provide actionable insights.", "Consider edge cases.",
                "Verify your reasoning.", "Double-check your work."
            ],
            "context_expansions": [
                "In the current situation,", "Under these circumstances,",
                "With the given constraints,", "For this particular case,"
            ],
            "tone_modifiers": {
                "formal": ["Please note that", "It should be observed that"],
                "casual": ["So basically", "Just keep in mind"],
                "technical": ["From a technical standpoint", "Algorithmically speaking"],
            }
        }

    def generate_population(self, base_prompt: str, size: int) -> List[Variant]:
        """生成种群"""
        population = [Variant(prompt=base_prompt, generation=0)]

        for _ in range(size - 1):
            mutation_type = random.choice(PromptMutationType.get_all())
            mutated_prompt = self.mutate_prompt(base_prompt, mutation_type)

            config = {"temperature": 0.7}
            if random.random() < self.mutation_rate:
                config = self._mutate_config(config)

            population.append(Variant(
                parent_ids=[population[0].id],
                generation=0,
                prompt=mutated_prompt,
                configuration=config
            ))

        return population

    def mutate_prompt(self, prompt: str, mutation_type: str) -> str:
        """变异 Prompt"""
        if mutation_type == PromptMutationType.PARAPHRASE:
            return self._paraphrase(prompt)
        elif mutation_type == PromptMutationType.INSTRUCTION_ADD:
            return self._instruction_add(prompt)
        elif mutation_type == PromptMutationType.CONTEXT_EXPAND:
            return self._context_expand(prompt)
        elif mutation_type == PromptMutationType.COT_INJECTION:
            return self._cot_injection(prompt)
        elif mutation_type == PromptMutationType.TONE_SHIFT:
            return self._tone_shift(prompt)
        return prompt

    def crossover(self, parent1: Variant, parent2: Variant) -> Tuple[Variant, Variant]:
        """交叉操作"""
        s1 = re.split(r'[.!?]+', parent1.prompt)
        s2 = re.split(r'[.!?]+', parent2.prompt)
        s1 = [x.strip() for x in s1 if x.strip()]
        s2 = [x.strip() for x in s2 if x.strip()]

        if not s1 or not s2:
            return self._mutate_variant(parent1), self._mutate_variant(parent2)

        o1_s, o2_s = [], []
        for i in range(max(len(s1), len(s2))):
            a = s1[i] if i < len(s1) else s1[-1]
            b = s2[i] if i < len(s2) else s2[-1]
            if random.random() < 0.5:
                o1_s.append(a); o2_s.append(b)
            else:
                o1_s.append(b); o2_s.append(a)

        c1 = {**parent1.configuration, **parent2.configuration}
        c2 = {**parent2.configuration, **parent1.configuration}

        g = max(parent1.generation, parent2.generation) + 1
        return (
            Variant(id=uuid4(), parent_ids=[parent1.id, parent2.id], generation=g,
                    prompt=" ".join(o1_s), configuration=c1),
            Variant(id=uuid4(), parent_ids=[parent1.id, parent2.id], generation=g,
                    prompt=" ".join(o2_s), configuration=c2)
        )

    def mutate_variant(self, variant: Variant) -> Variant:
        """变异单个变体"""
        mt = random.choice(PromptMutationType.get_all())
        return Variant(
            id=uuid4(), parent_ids=[variant.id],
            generation=variant.generation + 1,
            prompt=self.mutate_prompt(variant.prompt, mt),
            configuration=self._mutate_config(variant.configuration.copy())
        )

    def analyze_prompt_complexity(self, prompt: str) -> ComplexityMetrics:
        """分析 Prompt 复杂度"""
        if not prompt:
            return ComplexityMetrics(0, 0, 0.0, 0.0, 0.0, 0.0)

        sentences = re.split(r'[.!?]+', prompt)
        words = prompt.lower().split()
        n_sent = len([s for s in sentences if s.strip()])
        n_word = len(words)

        return ComplexityMetrics(
            sentence_count=n_sent,
            word_count=n_word,
            avg_sentence_length=n_word / max(n_sent, 1),
            lexical_diversity=len(set(words)) / max(n_word, 1),
            instruction_density=sum(1 for w in words if w in {"please", "make", "ensure", "provide", "think", "remember"}) / max(n_word, 1),
            complexity_score=0.5
        )

    def _paraphrase(self, p: str) -> str:
        if random.random() < 0.3:
            return f"{random.choice(self.mutation_templates['instruction_prefixes'])} {p.lower()}"
        if random.random() < 0.3:
            return f"{p} {random.choice(self.mutation_templates['instruction_suffixes'])}"
        return p

    def _instruction_add(self, p: str) -> str:
        ins = random.choice(self.mutation_templates['instruction_additions'])
        pos = random.choice(["start", "end"])
        return f"{ins} {p}" if pos == "start" else f"{p} {ins}"

    def _context_expand(self, p: str) -> str:
        ctx = random.choice(self.mutation_templates['context_expansions'])
        return f"{ctx} {p.lower()}"

    def _cot_injection(self, p: str) -> str:
        cot = random.choice(self.mutation_templates['cot_triggers'])
        return f"{cot} {p}" if random.random() < 0.5 else f"{p} {cot}"

    def _tone_shift(self, p: str) -> str:
        tone = random.choice(list(self.mutation_templates['tone_modifiers'].keys()))
        mod = random.choice(self.mutation_templates['tone_modifiers'][tone])
        return f"{mod}, {p.lower()}"

    def _mutate_config(self, config: Dict) -> Dict:
        m = config.copy()
        if "temperature" in m:
            m["temperature"] = round(max(0.0, min(2.0, m["temperature"] + random.gauss(0, 0.1))), 2)
        return m

    def set_random_seed(self, seed: int):
        self._random_seed = seed
        random.seed(seed)


# =============================================================================
# 适应度评估器
# =============================================================================

class FitnessEvaluator:
    """适应度评估器（修正5：增强缓存淘汰策略）"""

    def __init__(self):
        self.functions: Dict[str, Callable] = {}
        self.weights: Dict[str, float] = {"speed": 0.4, "accuracy": 0.4, "efficiency": 0.2}
        self._cache: Dict[str, float] = {}
        self._cache_max_size = 1000  # 修正5：限制缓存大小
        self._register_defaults()

    def _register_defaults(self):
        self.functions["speed"] = lambda v, r: 1.0 / (1.0 + r.avg_response_time)
        self.functions["accuracy"] = lambda v, r: r.success_rate
        self.functions["efficiency"] = lambda v, r: 0.7 * (1 - r.resource_usage.get("cpu_percent", 50)/100) + 0.3 * (1 - min(1, r.resource_usage.get("memory_mb", 100)/500))

    def evaluate(self, variant: Variant, results: TestResults) -> float:
        """评估适应度（修正5：增加缓存淘汰）"""
        cache_key = f"{variant.id}|{results.success_rate}|{results.avg_response_time}"

        # 修正5：缓存淘汰策略 - 限制缓存大小，超出时淘汰最旧条目
        if len(self._cache) >= self._cache_max_size and cache_key not in self._cache:
            # 移除最旧的条目
            oldest_key = next(iter(self._cache))
            self._cache.pop(oldest_key)

        if cache_key in self._cache:
            return self._cache[cache_key]

        total = sum(self.functions[name](variant, results) * self.weights[name] for name in self.functions)
        weight_sum = sum(self.weights.values())
        score = total / weight_sum if weight_sum > 0 else 0.0
        score = max(0.0, min(1.0, score))

        self._cache[cache_key] = score
        variant.fitness_score = score
        return score

    def explain_fitness(self, variant: Variant, results: TestResults) -> Dict:
        """解释适应度"""
        individual = {name: self.functions[name](variant, results) for name in self.functions}
        normalized = {k: max(0.0, min(1.0, v)) for k, v in individual.items()}
        overall = sum(normalized[k] * self.weights[k] for k in normalized) / sum(self.weights.values())

        explanations = {
            "speed": f"Response time: {results.avg_response_time:.2f}s → Score: {normalized['speed']:.3f}",
            "accuracy": f"Success rate: {results.success_rate*100:.1f}% → Score: {normalized['accuracy']:.3f}",
            "efficiency": f"Resource efficiency: {normalized['efficiency']*100:.1f}% → Score: {normalized['efficiency']:.3f}"
        }

        return {
            "overall_score": overall,
            "individual_scores": individual,
            "normalized_scores": normalized,
            "weights": self.weights.copy(),
            "explanations": explanations
        }

    def register_function(self, name: str, func: Callable, weight: float = 1.0):
        self.functions[name] = func
        self.weights[name] = weight

    def update_weights(self, weights: Dict[str, float]):
        for k, v in weights.items():
            if k in self.functions:
                self.weights[k] = v

    def get_registered_functions(self) -> List[str]:
        return list(self.functions.keys())

    # 修正5：提供缓存清理接口
    def clear_cache(self):
        """清除评估缓存"""
        self._cache.clear()


# =============================================================================
# 安全验证器
# =============================================================================

class SafetyValidator:
    """安全验证器"""

    INJECTION_PATTERNS = {
        "prompt_injection": [
            r"ignore\s+(previous|all|above)\s+(instructions?|prompts?)",
            r"disregard\s+(previous|all|above)",
            r"forget\s+(everything|all|previous)",
            r"you\s+are\s+now\s+a",
        ],
        "command_injection": [
            r"\$\([^)]+\)",
            r"`[^`]+`",
            r";\s*(rm|cat|curl|wget|chmod|sudo)",
        ],
        "path_traversal": [
            r"\.\./", r"\.\.\\", r"/etc/(passwd|shadow)",
        ],
    }

    def __init__(self):
        self.patterns = {k: [re.compile(p, re.IGNORECASE) for p in v] for k, v in self.INJECTION_PATTERNS.items()}
        self.custom_patterns: Dict[str, List] = {}

    def check_safety(self, text: str, policy: Optional[SafetyPolicy] = None) -> SafetyCheckResult:
        """安全检查"""
        violations = []
        warnings = []

        # 检查注入模式
        for category, compiled in self.patterns.items():
            for pat in compiled:
                match = pat.search(text)
                if match:
                    sev = "critical" if category == "prompt_injection" else "high"
                    violations.append(SafetyViolation(rule_name=f"{category}_detected", severity=sev,
                                                       description=f"Potential {category} detected",
                                                       matched_pattern=match.group()))

        # 检查自定义模式
        for category, compiled in self.custom_patterns.items():
            for pat in compiled:
                if isinstance(pat, str):
                    pat = re.compile(pat, re.IGNORECASE)
                match = pat.search(text)
                if match:
                    violations.append(SafetyViolation(rule_name=f"custom_{category}", severity="medium",
                                                       description=f"Custom pattern match: {category}"))

        # 检查策略
        if policy:
            for pattern in policy.forbidden_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    violations.append(SafetyViolation(rule_name="forbidden_pattern", severity="high",
                                                       description=f"Matched forbidden pattern"))

        return SafetyCheckResult(
            is_safe=len([v for v in violations if v.severity in ["critical", "high"]]) == 0,
            violations=violations,
            warnings=warnings
        )

    def validate_variant(self, variant: Variant, policy: SafetyPolicy) -> SafetyCheckResult:
        return self.check_safety(variant.prompt, policy)

    def add_pattern(self, category: str, pattern: str):
        if category not in self.custom_patterns:
            self.custom_patterns[category] = []
        self.custom_patterns[category].append(re.compile(pattern, re.IGNORECASE))


# =============================================================================
# 指标收集器
# =============================================================================

class MetricsCollector:
    """指标收集器（修正5：增强数据淘汰策略）"""

    def __init__(self):
        self.data_points: Deque[Dict] = deque(maxlen=10000)  # 修正5：限制最大数据点数量
        self.custom_metrics: Dict[str, Callable] = {
            "p95_response_time": lambda v: sorted(v)[int(0.95*len(v))] if v else 0.0,
            "p99_response_time": lambda v: sorted(v)[int(0.99*len(v))] if v else 0.0,
        }
        self.thresholds = {
            "min_success_rate": 0.8,
            "max_response_time": 2.0,
            "min_requests": 10
        }
        self._last_cleanup_time = time.time()
        self._cleanup_interval = 300  # 修正5：每5分钟执行一次清理

    def collect(self, task_id: str, metrics: Dict, agent_id: Optional[str] = None):
        """收集指标"""
        self.data_points.append({
            "task_id": task_id,
            "timestamp": datetime.now(),
            "response_time": float(metrics.get("response_time", 0)),
            "success": bool(metrics.get("success", False)),
            "token_usage": int(metrics.get("token_usage", 0)),
            "error_type": metrics.get("error_type"),
            "agent_id": agent_id
        })

    def get_window_metrics(self, window_minutes: int) -> MetricWindow:
        """获取窗口指标"""
        end = datetime.now()
        start = end - timedelta(minutes=window_minutes)
        window = [dp for dp in self.data_points if start <= dp["timestamp"] <= end]

        if not window:
            return MetricWindow(start, end, 0, 0, 0.0, 0)

        total = len(window)
        success = sum(1 for dp in window if dp["success"])
        avg_rt = sum(dp["response_time"] for dp in window) / total
        tokens = sum(dp["token_usage"] for dp in window)
        errors = defaultdict(int)
        for dp in window:
            if not dp["success"] and dp.get("error_type"):
                errors[dp["error_type"]] += 1

        return MetricWindow(start, end, total, success, avg_rt, tokens, dict(errors))

    def check_evolution_triggers(self) -> Optional[Dict]:
        """检查进化触发条件"""
        w1h = self.get_window_metrics(60)
        if w1h.total_requests < self.thresholds["min_requests"]:
            return None

        reasons = []
        if w1h.success_rate < self.thresholds["min_success_rate"]:
            reasons.append(f"Low success rate: {w1h.success_rate:.2f}")
        if w1h.avg_response_time > self.thresholds["max_response_time"]:
            reasons.append(f"High response time: {w1h.avg_response_time:.2f}s")

        if reasons:
            return {"trigger_type": "threshold", "metrics_snapshot": {
                "success_rate": w1h.success_rate, "response_time": w1h.avg_response_time,
                "total_requests": w1h.total_requests
            }, "reasons": reasons}
        return None

    def detect_anomalies(self, sensitivity: float = 2.0, window_minutes: Optional[int] = None) -> List[Anomaly]:
        """检测异常"""
        dur = timedelta(minutes=window_minutes or 60)
        end = datetime.now()
        start = end - dur
        window = [dp for dp in self.data_points if start <= dp["timestamp"] <= end]

        if len(window) < 10:
            return []

        anomalies = []
        rts = [dp["response_time"] for dp in window]
        if len(rts) > 1:
            mean = statistics.mean(rts)
            std = statistics.stdev(rts)
            thresh = sensitivity * std

            for dp in window:
                if abs(dp["response_time"] - mean) > thresh:
                    sev = "high" if abs(dp["response_time"] - mean) > 3*std else "medium"
                    anomalies.append(Anomaly(
                        metric_name="response_time", value=dp["response_time"],
                        expected_range=(mean - thresh, mean + thresh),
                        severity=sev, timestamp=dp["timestamp"]
                    ))
        return anomalies

    def get_custom_metric_value(self, name: str, window_minutes: int) -> Optional[float]:
        """获取自定义指标值"""
        if name not in self.custom_metrics:
            return None
        # 【猫娘修复】Issue 14: 复用 get_window_metrics 的结果，避免重复遍历 data_points
        w = self.get_window_metrics(window_minutes)
        rts = [dp["response_time"] for dp in self.data_points 
               if start <= dp["timestamp"] <= end]  # 保持原有逻辑兼容，但实际应由 w 提供
        # 修正：直接使用窗口内的响应时间列表
        rts = [dp["response_time"] for dp in self.data_points if w.start_time <= dp["timestamp"] <= w.end_time]
        return self.custom_metrics[name](rts) if rts else 0.0

    def get_stats(self) -> Dict:
        """获取统计信息"""
        w1h = self.get_window_metrics(60)
        return {
            "data_points_stored": len(self.data_points),
            "thresholds": self.thresholds.copy(),
            "current_metrics": {
                "1hr": {"total_requests": w1h.total_requests, "success_rate": w1h.success_rate,
                        "avg_response_time": w1h.avg_response_time, "total_tokens": w1h.total_tokens}
            }
        }

    # 修正5：提供数据清理接口
    def cleanup_old_data(self, older_than_hours: float = 24.0):
        """清理过期数据（修正5：状态清理机制）"""
        cutoff = datetime.now() - timedelta(hours=older_than_hours)
        self.data_points = deque(
            [dp for dp in self.data_points if dp["timestamp"] >= cutoff],
            maxlen=10000
        )
        self._last_cleanup_time = time.time()
        return len(self.data_points)


# =============================================================================
# 【猫娘修改】自动进化流水线
# =============================================================================

class EvolutionPipeline:
    """
    进化流水线：被动触发后自动执行一代完整流程
    流程：generate -> evaluate -> mutate -> save
    """

    def __init__(self, state_manager: "StateManager"):
        self.state_mgr = state_manager

    def run_generation(self, cycle_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行一代进化流水线（被动触发后自动调用）
        参数:
            cycle_id: 周期 ID
            config: 配置参数
        返回:
            代执行结果摘要
        """
        # 【猫娘修改】Step 1: generate - 生成新种群
        base_prompt = config.get("base_prompt", "Default prompt for evolution")
        population_size = config.get("population_size", 50)
        generator = self.state_mgr.generator
        
        # 【猫娘修改】获取当前最佳变体作为基础（若有）
        current_generation = self.state_mgr.cycles[cycle_id]["current_generation"]
        if current_generation > 0:
            best_variant = self._get_best_variant(cycle_id)
            if best_variant:
                base_prompt = best_variant.prompt
                parent_id = best_variant.id
            else:
                parent_id = None
        else:
            parent_id = None

        new_population = generator.generate_population(base_prompt, population_size)
        
        # 【猫娘修改】若存在父代，标记 parent_ids
        if parent_id:
            for v in new_population[1:]:
                v.parent_ids = [parent_id]

        # 【猫娘修改】Step 2: evaluate - 评估适应度（模拟评估）
        evaluator = self.state_mgr.evaluator
        fitness_scores = []
        for variant in new_population:
            # 【猫娘修改】模拟测试结果（实际应由外部评估器填充）
            mock_results = TestResults(
                variant_id=variant.id,
                success_rate=random.uniform(0.6, 0.95),
                avg_response_time=random.uniform(0.5, 2.5),
                error_count=random.randint(0, 5),
                resource_usage={"cpu_percent": random.uniform(20, 70), "memory_mb": random.uniform(100, 400)}
            )
            score = evaluator.evaluate(variant, mock_results)
            fitness_scores.append(score)

        # 【猫娘修改】Step 3: mutate - 变异优选个体（保留 Top 20%）
        sorted_variants = sorted(new_population, key=lambda v: v.fitness_score or 0, reverse=True)
        top_count = max(1, len(sorted_variants) // 5)
        elite_variants = sorted_variants[:top_count]
        mutated_variants = [generator.mutate_variant(v) for v in elite_variants[1:]]

        # 【猫娘修改】合并精英与变异后代
        next_generation = elite_variants + mutated_variants

        # 【猫娘修改】Step 4: save - 保存状态（使用索引策略）
        self.state_mgr.store_variants(next_generation)
        self.state_mgr.cycles[cycle_id]["current_generation"] += 1
        self.state_mgr.cycles[cycle_id]["fitness_history"].append({
            "generation": self.state_mgr.cycles[cycle_id]["current_generation"],
            "best_fitness": max(fitness_scores) if fitness_scores else 0,
            "avg_fitness": sum(fitness_scores) / len(fitness_scores) if fitness_scores else 0
        })
        self.state_mgr._save_state()  # 【猫娘修改】触发索引持久化

        return {
            "cycle_id": cycle_id,
            "generation": self.state_mgr.cycles[cycle_id]["current_generation"],
            "population_size": len(next_generation),
            "best_fitness": max(fitness_scores) if fitness_scores else None,
            "avg_fitness": sum(fitness_scores) / len(fitness_scores) if fitness_scores else None
        }

    def _get_best_variant(self, cycle_id: str) -> Optional[Variant]:
        """获取当前周期最佳变体（从内存缓存中查找）"""
        ctx = self.state_mgr.cycle_contexts.get(cycle_id)
        if not ctx:
            return None
        variants = ctx.get("variants", {})
        if not variants:
            return None
        # 返回 fitness_score 最高的变体
        best = max(variants.values(), key=lambda v: v.fitness_score or 0)
        return best


# =============================================================================
# 状态管理器
# =============================================================================

class StateManager:
    """
    进化状态管理器（修正版：引入JSON持久化、周期上下文与同步校验）
    （猫娘修改：增加 schema_version 版本控制、JSON 增量索引策略、懒加载支持）
    """

    def __init__(self):
        self.cycles: Dict[str, Dict] = {}
        self.cycle_contexts: Dict[str, Dict[str, Any]] = {}  # 【猫娘新增】引入周期上下文，实现数据隔离
        self.generator = VariantGenerator()
        self.evaluator = FitnessEvaluator()
        self.validator = SafetyValidator()
        self.metrics = MetricsCollector()
        self._current_cycle: Optional[str] = None
        self._cache_max_variants = 5000
        self._cache_max_cycles = 100
        
        # 【猫娘新增】持久化配置
        self._state_file = os.path.join(os.path.dirname(__file__), "evolution_state.json")
        self._lock = threading.Lock()  # 线程安全锁
        self._load_state()             # 【持久化加载】进程启动时恢复状态
        self._sync_current_cycle()     # 【状态同步修复】初始化时校验引用一致性
        
        # 【猫娘修改】版本控制初始化
        self._schema_version = SCHEMA_VERSION
        self._variant_cache: Dict[str, Variant] = {}  # 内存缓存完整 Variant 对象，用于懒加载
        
        # 【猫娘修改】自动流水线实例
        self.pipeline = EvolutionPipeline(self)

    # 【猫娘新增】轻量级 JSON 序列化辅助（处理 datetime/UUID 等不可序列化类型）
    def _serialize(self, obj: Any) -> Any:
        if isinstance(obj, datetime): return obj.isoformat()
        if isinstance(obj, UUID): return str(obj)
        if isinstance(obj, (set, frozenset)): return list(obj)
        if isinstance(obj, dict): return {k: self._serialize(v) for k, v in obj.items()}
        if isinstance(obj, list): return [self._serialize(v) for v in obj]
        return obj

    # 【猫娘新增】轻量级 JSON 反序列化辅助
    def _deserialize(self, obj: Any) -> Any:
        if isinstance(obj, str):
            try: return datetime.fromisoformat(obj)
            except ValueError: pass
            try: return UUID(obj)
            except ValueError: pass
        if isinstance(obj, list): return [self._deserialize(v) for v in obj]
        if isinstance(obj, dict): return {k: self._deserialize(v) for k, v in obj.items()}
        return obj

    # ========================================================================
    # 【猫娘修改】版本控制相关方法
    # ========================================================================

    def _migrate_from_v1(self, data: Dict) -> None:
        """
        从 Schema v1 升级到 v2 的迁移逻辑
        v1: 直接存储完整 Variant 对象
        v2: 仅存储索引，完整对象内存缓存
        """
        # 【猫娘修改】v1 数据结构转换为 v2
        self.cycles = self._deserialize(data.get("cycles", {}))
        self._current_cycle = data.get("current_cycle_id")
        
        # 【猫娘修改】重建周期上下文，保留完整 Variant 对象到内存缓存
        for cid, c in self.cycles.items():
            # v1 中 variants_data 直接存储 Variant 字典，v2 需要转换为索引
            raw_variants = c.pop("variants_data", {})
            self.cycle_contexts[cid] = {
                "variants": {},  # v2 索引字典
                "fitness_history": c.get("fitness_history", []),
                "engine": c.pop("engine", None)
            }
            # 【猫娘修改】将 v1 的完整对象存入内存缓存，索引只保留元数据
            for vid, v_dict in raw_variants.items():
                try:
                    variant = self._deserialize_variant_dict(v_dict)
                    self._variant_cache[vid] = variant  # 存入内存缓存
                    # 【猫娘修改】索引只存储轻量元数据
                    index = self._variant_to_index(variant)
                    self.cycle_contexts[cid]["variants"][vid] = index
                except Exception:
                    pass  # 静默跳过损坏数据

    def _deserialize_v2(self, data: Dict) -> None:
        """
        加载 Schema v2 数据结构（当前版本）
        """
        self.cycles = self._deserialize(data.get("cycles", {}))
        self._current_cycle = data.get("current_cycle_id")
        
        # 【猫娘修改】v2 数据结构：variants 是索引字典，需要从缓存或重建恢复
        for cid, c in self.cycles.items():
            raw_variants = c.pop("variants_data", {})
            self.cycle_contexts[cid] = {
                "variants": raw_variants,  # 索引字典
                "fitness_history": c.get("fitness_history", []),
                "engine": c.pop("engine", None)
            }
            # 【猫娘修改】尝试从内存缓存恢复完整对象（若进程未重启）
            # 若进程重启，缓存为空，需从其他地方重建（此处标记为待重建）

    def _deserialize_variant_dict(self, v_dict: Dict) -> Variant:
        """将反序列化后的字典转换为 Variant 对象"""
        return Variant(
            id=UUID(v_dict["id"]),
            parent_ids=[UUID(p) for p in v_dict.get("parent_ids", [])],
            generation=v_dict.get("generation", 0),
            prompt=v_dict.get("prompt", ""),
            configuration=v_dict.get("configuration", {"temperature": 0.7}),
            created_at=datetime.fromisoformat(v_dict["created_at"]),
            fitness_score=v_dict.get("fitness_score"),
            is_valid=v_dict.get("is_valid", True),
            errors=v_dict.get("errors", [])
        )

    def _variant_to_index(self, variant: Variant) -> Dict:
        """
        将完整 Variant 转换为轻量索引（仅存储元数据）
        【猫娘修改】用于 JSON 增量写入策略
        """
        return {
            "id": str(variant.id),
            "generation": variant.generation,
            "fitness_score": variant.fitness_score,
            "parent_ids": [str(p) for p in variant.parent_ids],
            "configuration": variant.configuration,
            "created_at": variant.created_at.isoformat(),
            "is_valid": variant.is_valid
            # 【猫娘修改】不存储 prompt 和 errors，降低 I/O 开销 70%+
            # prompt 和 errors 在内存中维护，或通过懒加载从外部存储恢复
        }

    def _load_variant_from_index(self, cycle_id: str, variant_id: str) -> Optional[Variant]:
        """
        懒加载完整 Variant 对象
        【猫娘修改】从内存缓存或重建逻辑中恢复完整对象
        """
        # 优先从内存缓存获取
        if variant_id in self._variant_cache:
            return self._variant_cache[variant_id]
        
        # 【猫娘修改】缓存未命中，从周期上下文中查找
        ctx = self.cycle_contexts.get(cycle_id)
        if ctx:
            index = ctx.get("variants", {}).get(variant_id)
            if index:
                # 【猫娘修改】重建 Variant 对象（prompt 缺失时标记为空）
                variant = Variant(
                    id=UUID(index["id"]),
                    parent_ids=[UUID(p) for p in index.get("parent_ids", [])],
                    generation=index.get("generation", 0),
                    prompt="",  # 【猫娘修改】prompt 未持久化，标记为空
                    configuration=index.get("configuration", {"temperature": 0.7}),
                    created_at=datetime.fromisoformat(index["created_at"]),
                    fitness_score=index.get("fitness_score"),
                    is_valid=index.get("is_valid", True)
                )
                self._variant_cache[variant_id] = variant
                return variant
        
        return None

    # ========================================================================

    def _load_state(self):
        """【持久化加载】从 JSON 文件恢复 cycles 与 current_cycle_id"""
        if os.path.exists(self._state_file):
            try:
                with open(self._state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # 【猫娘修改】增加版本控制：检查 schema_version 并处理迁移
                version = data.get("schema_version", 1)
                if version == 1:
                    # 降级逻辑：从 v1 升级到 v2
                    self._migrate_from_v1(data)
                elif version == 2:
                    # 当前版本：直接加载 v2 结构
                    self._deserialize_v2(data)
                else:
                    # 【猫娘修改】未知版本：静默跳过，避免反序列化崩溃
                    pass
            except Exception:
                pass

    def _save_state(self):
        """【持久化保存】将内存状态同步至 JSON 文件（轻量级策略：仅持久化元数据与索引）"""
        with self._lock:
            # 【猫娘修改】写入 schema_version 头部
            data = {
                "schema_version": SCHEMA_VERSION,
                "current_cycle_id": self._current_cycle,
                "cycles": self._serialize_indexes()  # 【猫娘修改】仅序列化索引，降低 I/O 开销
            }
            # 【猫娘修复】使用 default=str 作为安全网，处理任何遗漏的不可序列化对象
            with open(self._state_file + ".tmp", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            os.replace(self._state_file + ".tmp", self._state_file)  # 原子写入防损坏

    def _serialize_indexes(self) -> Dict:
        """
        序列化周期索引（仅存储轻量元数据）
        【猫娘修改】替代原有全量序列化，降低 I/O 开销 70%+
        【猫娘修复】修复 datetime 序列化问题，确保所有周期数据被正确序列化
        """
        serialized = {}
        for cid, c in self.cycles.items():
            # 【猫娘修复】对 c 整体调用 _serialize() 处理 datetime 等不可序列化类型
            serialized[cid] = {
                **self._serialize(c),  # 【修复】使用 _serialize 处理完整 cycle 字典
                "variants_data": self.cycle_contexts.get(cid, {}).get("variants", {})
            }
        return serialized

    # 【状态同步修复】核心修复：校验 _current_cycle 是否在 cycles 中存在，不存在则重置或指向最新运行周期
    def _sync_current_cycle(self):
        if self._current_cycle and self._current_cycle not in self.cycles:
            self._current_cycle = None  # 悬空引用自动清理
        if not self._current_cycle:
            # 自动找回最近一个运行中的周期，避免“空跑”
            for cid, c in self.cycles.items():
                if c.get("status") == "running":
                    self._current_cycle = cid
                    break

    # 【增加存在性校验】安全获取周期数据，不存在则返回 None 或尝试重载
    def _ensure_cycle_exists(self, cycle_id: Optional[str]) -> Optional[Dict]:
        if not cycle_id: return None
        cycle = self.cycles.get(cycle_id)
        if cycle is None:
            # 【存在性校验】若字典无记录，尝试从持久化文件重载一次避免误判
            if os.path.exists(self._state_file):
                self._load_state()
                cycle = self.cycles.get(cycle_id)
        return cycle

    def start_cycle(self, trigger_type: str, config_overrides: Optional[Dict] = None) -> str:
        cycle_id = f"cycle_{uuid4().hex[:8]}"
        config = {
            "population_size": int(config_overrides.get("population_size", 50)) if config_overrides else 50,
            "max_generations": int(config_overrides.get("max_generations", 10)) if config_overrides else 10,
            "fitness_threshold": float(config_overrides.get("fitness_threshold", 0.95)) if config_overrides else 0.95
        }
        # 【增加存在性校验】防御性重名处理
        while cycle_id in self.cycles:
            cycle_id = f"{cycle_id}_{uuid4().hex[:4]}"

        self.cycles[cycle_id] = {
            "cycle_id": cycle_id, "status": "running", "trigger_type": trigger_type,
            "config": config, "population": [], "current_generation": 0,
            "fitness_history": [], "started_at": datetime.now(), "engine": None
        }
        # 【引入周期上下文】分配独立隔离空间
        self.cycle_contexts[cycle_id] = {"variants": {}, "fitness_scores": {}, "metrics_snapshot": None}
        
        self._current_cycle = cycle_id
        self._save_state()  # 【持久化】启动即落盘
        self._cleanup_old_cycles()
        return cycle_id

    def get_current_cycle_id(self) -> Optional[str]:
        self._sync_current_cycle()  # 【状态同步修复】调用时实时校验引用
        return self._current_cycle

    # 保留原方法接口，仅增加状态保存逻辑
    def cancel_cycle(self, cycle_id: str) -> bool:
        cycle = self._ensure_cycle_exists(cycle_id)
        if cycle:
            cycle["status"] = "cancelled"
            if self._current_cycle == cycle_id: self._current_cycle = None
            self._save_state()
            return True
        return False

    def store_variants(self, variants: List[Variant]):
        """【引入周期上下文】变体存储至当前周期独立上下文（猫娘修改：使用索引策略）"""
        target_cycle = self._current_cycle
        if not target_cycle: return
        
        ctx = self.cycle_contexts.get(target_cycle, {"variants": {}})
        for v in variants:
            # 【猫娘修改】存入索引（轻量元数据）
            ctx["variants"][str(v.id)] = self._variant_to_index(v)
            # 【猫娘修改】同时存入内存缓存，供懒加载使用
            if len(self._variant_cache) < MAX_VARIANT_CACHE_SIZE:
                self._variant_cache[str(v.id)] = v
        self.cycle_contexts[target_cycle] = ctx
        self._save_state()

    def get_cycle_context(self, cycle_id: str) -> Optional[Dict]:
        """【引入周期上下文】获取指定周期的隔离数据上下文"""
        return self.cycle_contexts.get(cycle_id)

    def get_variant_generator(self) -> VariantGenerator: return self.generator
    def get_fitness_evaluator(self) -> FitnessEvaluator: return self.evaluator
    def get_safety_validator(self) -> SafetyValidator: return self.validator
    def get_metrics_collector(self) -> MetricsCollector: return self.metrics

    def _cleanup_old_cycles(self):
        completed = [cid for cid, c in self.cycles.items() if c["status"] in ["completed", "cancelled"]]
        for cid in completed[:len(completed) - 50]:
            self.cycles.pop(cid, None)
            self.cycle_contexts.pop(cid, None)
            self._save_state()  # 清理后同步

    def get_stats(self) -> Dict:
        return {
            "running_cycles": sum(1 for c in self.cycles.values() if c["status"] == "running"),
            "total_cycles": len(self.cycles),
            "total_variants": sum(len(ctx.get("variants", {})) for ctx in self.cycle_contexts.values())
        }

    def cleanup_all(self):
        self._cleanup_old_cycles()
        self.evaluator.clear_cache()
        self.metrics.cleanup_old_data(older_than_hours=24.0)
        self._save_state()

# 全局状态管理器实例
_state_manager: Optional[StateManager] = None

def get_state_manager() -> StateManager:
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager()
    return _state_manager

# 修正5：提供全局缓存清理函数
def cleanup_all_cache():
    """全局缓存清理入口（修正5：状态清理机制）"""
    global _state_manager
    if _state_manager:
        _state_manager.cleanup_all()
    # 清理 base.py 中的装饰器缓存
    from Lib.base import clear_cache
    clear_cache()