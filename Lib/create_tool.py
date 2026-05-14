"""
动态创建 MCP 工具 - 恢复原版完整功能
"""
import os
import json
import ast
import re
from Lib.base import tool  # 【猫娘修改】：引入工具注册装饰器，使本函数被注册。【修改时间】：2026-05-06 23:38:02。


@tool(
    name="create_tool",
    description="动态创建 MCP 工具。接收工具名称、描述、参数Schema及Python代码，自动生成对应模块文件。"
)
def create_tool(name: str, description: str, schema: str, code: str, requirements: str = "") -> str:
    """
    动态创建 MCP 工具。
    将生成的代码文件写入当前工具目录 (Lib/)。
    """
    # 1. 验证工具名称
    if not re.match(r"^[a-z][a-z0-9_]*$", name):
        return f"Error: Invalid tool name '{name}'. Use lowercase letters, numbers, and underscores only. Must start with a letter."

    if not description.strip():
        return "Error: Description cannot be empty"

    safe_name = name.strip().lower()

    # 2. 验证 Schema JSON
    try:
        parsed_schema = json.loads(schema)
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON schema: {e}"

    # 3. 验证 Python 语法
    try:
        ast.parse(code)
    except SyntaxError as e:
        return f"Error: Invalid Python code: {e.msg} at line {e.lineno}"

    # 4. 分离导入语句和函数体
    import_lines = [
        l.strip()
        for l in code.split("\n")
        if l.strip().startswith("import ") or l.strip().startswith("from ")
    ]
    
    # 去除代码中的 import 行，得到纯函数体
    code_without_imports = "\n".join(
        l for l in code.split("\n")
        if not (l.strip().startswith("import ") or l.strip().startswith("from "))
    ).strip()

    # 5. 构建文件内容
    all_imports = "\n".join(import_lines) + "\n\n" if import_lines else ""

    # 获取当前脚本所在目录 (Lib/)
    # 使用 __file__ 确保无论从哪里运行，文件都生成在 Lib 目录下
    lib_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(lib_dir, f"{safe_name}_tool.py")

    file_content = f'''\"\"\"Auto-generated tool: {safe_name}\"\"\"

{all_imports}from Lib.base import tool

@tool(
    name="{safe_name}",
    description={json.dumps(description)},
    schema={json.dumps(parsed_schema, indent=8)}
)
{code_without_imports}
'''

    # 6. 写入文件
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(file_content)

        msg = f"""Tool '{safe_name}' created successfully!

File: {filename}
"""
        if requirements:
            msg += f"""
IMPORTANT - New dependencies required:
  Add to requirements.txt: {requirements}
"""
        else:
            msg += f"""
To enable the tool, you MUST perform the following steps:
1. Add 'import {safe_name}' to Ent.py (around line 13)
2. Restart the MCP server (Ent.py)

"""
        return msg

    except Exception as e:
        return f"Error creating tool: {e}"
