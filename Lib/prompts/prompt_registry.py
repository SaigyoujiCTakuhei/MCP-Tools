"""
提示词注册模块
-------------
统一负责提示词模板加载与 MCP 装饰器注册。
遵循项目架构规范：相关功能统一放入同一文件夹。

目录结构：
- Lib/prompts/__init__.py          # 模块初始化
- Lib/prompts/prompt_registry.py   # 提示词加载与注册逻辑
- Lib/prompts/*.txt                # 提示词模板文件
"""
import os
from mcp.server.fastmcp import FastMCP

# ========== 提示词模板加载 ==========
PROMPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "")

def load_prompt(name: str) -> str:
    """【猫娘修改】：从 Lib/prompts/ 目录加载提示词模板。【修改时间】：2026-05-14 17:02:00。"""
    try:
        prompt_path = os.path.join(PROMPTS_DIR, f"{name}.txt")
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise ValueError(f"Prompt template not found: {name}")
    except Exception as e:
        raise ValueError(f"Failed to load prompt {name}: {e}")


def register_prompts(mcp_instance: FastMCP):
    """【猫娘修改】：注册所有提示词到 MCP 实例。【修改时间】：2026-05-14 17:02:00。"""
    try:
        @mcp_instance.prompt(name="refactor_mcp_project")
        def refactor_mcp_project(
            source_path: str,
            target_path: str,
            code_type: str = "Python"
        ) -> str:
            """【猫娘修改】：重构 MCP 项目提示词 - 按架构重写、拆分、适配装饰器。【修改时间】：2026-05-14 17:02:00。"""
            template = load_prompt("refactor_mcp_project")
            return template.format(
                source_path=source_path,
                target_path=target_path,
                code_type=code_type
            )

        @mcp_instance.prompt(name="create_prompt_template")
        def create_prompt_template(
            prompt_name: str,
            prompt_description: str,
            prompt_arguments: str = "{}",
            template_content: str = ""
        ) -> str:
            """【猫娘修改】：创建新提示词模板 - 用于方便之后添加提示词模板。【修改时间】：2026-05-14 17:02:00。"""
            template = load_prompt("create_prompt_template")
            return template.format(
                prompt_name=prompt_name,
                prompt_description=prompt_description,
                prompt_arguments=prompt_arguments,
                template_content=template_content
            )

        # 【猫娘修改】：使用正确方式统计注册的提示词数量。【修改时间】：2026-05-14 17:02:00。
        prompt_count = len(mcp_instance._prompt_manager._prompts) if hasattr(mcp_instance._prompt_manager, '_prompts') else 0
        print(f"  [PROMPT-REGISTRY] Registered {prompt_count} prompt(s)")
        
    except Exception as e:
        print(f"  [PROMPT-REGISTRY] ERROR: {e}")
        raise
