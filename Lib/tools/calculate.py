"""
Perform mathematical calculations
"""
import os
import sys
import json
import ast
import math

from Lib.base.base import tool

@tool(
    name="calculate",
    description="Perform mathematical calculations",
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
        # 【猫娘修复】Issue 5: 增加 AST 语法树白名单校验，防止 eval 沙箱逃逸
        tree = ast.parse(expression, mode='eval')
        allowed_nodes = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Name, 
                        ast.Load, ast.Constant, ast.Attribute)
        for node in ast.walk(tree):
            if not isinstance(node, allowed_nodes):
                return "Error: Expression contains unsafe operations or syntax"
        
        allowed = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
        allowed.update({"abs": abs, "round": round, "min": min, "max": max, "pow": pow})
        return str(eval(expression, {"__builtins__": {}, **allowed}))
    except SyntaxError as e: return f"Error: Invalid syntax - {e.msg}"
    except Exception as e: return f"Error: {e}"