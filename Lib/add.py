"""
Add two numbers
（修正2：采用显式包导入）
"""
from Lib.base import tool

@tool(
    name="add",
    description="Add two numbers",
    schema={
    "type": "object",
    "properties": {
        "a": {
            "type": "integer"
        },
        "b": {
            "type": "integer"
        }
    },
    "required": [
        "a",
        "b"
    ]
}
)
def add(a: int, b: int) -> int:
    return a + b
