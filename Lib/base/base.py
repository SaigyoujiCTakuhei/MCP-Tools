"""
基础工具装饰器
"""
import inspect
import json
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

# ========== 缓存淘汰机制（修正5：引入 LRU 缓存淘汰策略） ==========
_CACHE_TTL = 3600  # 缓存生存时间（秒），默认1小时
_MAX_CACHE_SIZE = 500  # 最大缓存条目数
_cache_store: OrderedDict[str, tuple] = OrderedDict()  # 缓存存储：key -> (value, expire_time)


def _cache_cleanup():
    """清理过期缓存条目，同时维持最大缓存容量"""
    current_time = time.time()
    # 先清理过期条目
    expired_keys = [k for k, (v, exp) in _cache_store.items() if exp < current_time]
    for k in expired_keys:
        _cache_store.pop(k, None)

    # 再维持最大容量（淘汰最久未使用的）
    while len(_cache_store) > _MAX_CACHE_SIZE:
        _cache_store.popitem(last=False)  # 移除最旧的条目


def cache(ttl: int = _CACHE_TTL, max_size: int = _MAX_CACHE_SIZE):
    """
    LRU 缓存装饰器（修正5：引入缓存淘汰机制）
    :param ttl: 缓存生存时间（秒）
    :param max_size: 最大缓存条目数
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # 【猫娘修复】Issue 4: 使用 json.dumps 生成稳定缓存键，避免因可变对象字符串表示不同导致缓存失效
            safe_args = json.dumps(args, default=lambda x: str(x), sort_keys=True)
            safe_kwargs = json.dumps(kwargs, default=lambda x: str(x), sort_keys=True)
            cache_key = f"{func.__name__}:{safe_args}:{safe_kwargs}"
            _cache_cleanup()  # 每次访问前执行清理

            if cache_key in _cache_store:
                value, expire_time = _cache_store[cache_key]
                if expire_time > time.time():
                    _cache_store.move_to_end(cache_key)  # 更新访问顺序
                    return value

            result = func(*args, **kwargs)
            _cache_store[cache_key] = (result, time.time() + ttl)
            _cache_store.move_to_end(cache_key)

            # 超出容量时淘汰最旧条目
            if len(_cache_store) > max_size:
                _cache_store.popitem(last=False)

            return result
        return wrapper
    return decorator


def clear_cache():
    """清除所有缓存（修正5：提供状态清理接口）"""
    _cache_store.clear()
# ====================================================================


@dataclass
class ToolDefinition:
    name: str
    description: str
    func: Callable
    input_schema: dict
    _metadata: dict = field(default_factory=dict)  # 扩展元数据（如缓存配置）


class ToolRegistry:
    _tools: dict[str, ToolDefinition] = {}

    @classmethod
    def register(cls, name: str, description: str, func: Callable, input_schema: dict, **metadata):
        """注册工具，支持扩展元数据（修正5：增加元数据支持）"""
        cls._tools[name] = ToolDefinition(
            name=name, description=description, func=func, input_schema=input_schema,
            _metadata=metadata
        )

    @classmethod
    def get_all(cls) -> dict[str, ToolDefinition]:
        return cls._tools.copy()

    @classmethod
    def get(cls, name: str) -> Optional[ToolDefinition]:
        return cls._tools.get(name)

    @classmethod
    def clear(cls):
        """清除所有注册的工具（修正5：提供状态清理接口）"""
        cls._tools.clear()


def tool(name: str, description: str, schema: dict | None = None):
    """工具装饰器 - 将函数注册到 ToolRegistry"""
    def decorator(func: Callable) -> Callable:
        nonlocal schema  # 【修正】声明为非局部变量，解决 Python 闭包作用域导致的 UnboundLocalError
        # 自动从函数签名生成 schema（如果未提供）
        if not schema:
            schema = _infer_schema(func)

        ToolRegistry.register(name, description, func, schema)
        return func
    return decorator


def _infer_schema(func: Callable) -> dict:
    """从函数签名自动推断 JSON Schema（修正2：显式包导入方式下的辅助函数）"""
    import inspect
    sig = inspect.signature(func)
    properties = {}
    required = []
    for param_name, param in sig.parameters.items():
        # 跳过 self 和 cls
        if param_name in ('self', 'cls'):
            continue
        param_type = param.annotation
        if param_type == inspect.Parameter.empty:
            param_type = str

        type_mapping = {
            int: "integer",
            float: "number",
            str: "string",
            bool: "boolean",
            list: "array",
            dict: "object",
        }
        json_type = type_mapping.get(param_type, "string")

        properties[param_name] = {"type": json_type}
        if param.default == inspect.Parameter.empty:
            required.append(param_name)

    return {
        "type": "object",
        "properties": properties,
        "required": required
    }


# 【移除模块】已删除 get_tools_from_module 函数（保持接口精简）
# 该函数未被项目使用，已移除以避免 API 冗余