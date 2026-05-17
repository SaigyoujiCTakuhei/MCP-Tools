"""
Perform mathematical calculations
"""
import os
import sys
import json
import math
import re  # 【猫娘修改】：引入 re 模块用于 ^ 符号预处理

from Lib.base.base import tool

@tool(
    name="calculate",
    description="Perform mathematical calculations. Enhanced version supports ^ as exponent operator.",
    schema={
    "type": "object",
    "properties": {
        "expression": {
            "type": "string",
            "description": "Math expression"
        }
    },
    "required": [
        "expression"
    ]
}
)
def calculate(expression: str) -> str:
    try:
        # 【猫娘修改】：修复 ^ 符号在 Python 中被解析为异或的问题，安全替换为幂运算 **
        # 使用正则精准匹配数学上下文中的 ^，避免误伤字符串或变量名
        safe_expr = re.sub(r'(?<=[\d\w\)\]])\^(?=[\d\(])', '**', expression)
        
        # 【猫娘修改】：合并原有白名单与增强型动态提取，确保兼容性与完整性
        allowed = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
        allowed.update({
            "abs": abs, "round": round, "min": min, "max": max, "pow": pow,
            "sum": sum, "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "pi": math.pi, "e": math.e,
            "floor": math.floor, "ceil": math.ceil, "trunc": math.trunc,
            "exp": math.exp, "log2": math.log2
        })
        return str(eval(safe_expr, {"__builtins__": {}, **allowed}))
    except SyntaxError as e: return f"Error: Invalid syntax - {e.msg}"
    except Exception as e: return f"Error: {e}"
