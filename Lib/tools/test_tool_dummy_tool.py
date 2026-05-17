"""Auto-generated tool: test_tool_dummy"""

from Lib.base.base import tool

@tool(
    name="test_tool_dummy",
    description="Dummy test tool for schema validation only",
    schema={
        "type": "object",
        "properties": {
                "test": {
                        "type": "string"
                }
        },
        "required": [
                "test"
        ]
}
)
def test_tool_dummy(test: str):
    return {"echo": test}
