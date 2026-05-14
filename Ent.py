"""
MCP 服务器主入口
"""
import sys
import inspect
import os
import importlib
from typing import Optional

from mcp.server.fastmcp import FastMCP
from Lib.base import ToolRegistry

# ========== 基础工具导入 =========
from Lib import add
from Lib import get_current_date
from Lib import get_everything_info
from Lib import search
from Lib import complex_search
from Lib import read_file
from Lib import write_file
from Lib import list_directory
from Lib import search_files
from Lib import run_command
from Lib import web_search
from Lib import web_fetch
from Lib import python_eval
from Lib import git_clone
from Lib import git_pull
from Lib import get_system_info
from Lib import grep
from Lib import get_time
from Lib import calculate
from Lib import manage_blacklist
from Lib import manage_approved
from Lib import get_dangerous_patterns
from Lib import create_tool
from Lib import count_lines
from Lib import download_file
from Lib import file_info
from Lib import create_directory
from Lib import delete_file
from Lib import run_python_script
from Lib import hello_world
from Lib import reverse_text
from Lib import get_weather

# ========== Evolve-MCP 工具导入 ==========
from Lib import start_evolution
from Lib import get_evolution_status
from Lib import cancel_evolution
from Lib import resume_evolution
from Lib import generate_population
from Lib import mutate_prompt
from Lib import crossover_variants
from Lib import generate_ab_pair
from Lib import analyze_prompt
from Lib import evaluate_variant
from Lib import explain_fitness
from Lib import register_fitness_function
from Lib import update_fitness_weights
from Lib import list_fitness_functions
from Lib import validate_variant
from Lib import check_safety
from Lib import add_safety_pattern
from Lib import record_metrics
from Lib import get_metrics_window
from Lib import check_evolution_trigger
from Lib import detect_anomalies
# ========================================

# 创建 FastMCP 实例
mcp = FastMCP(
    "Ent MCP Server",
    host="127.0.0.1",
    port=58000,
    stateless_http=True,
    json_response=True,
)


def _auto_scan_lib_tools():
    """【猫娘修复】Issue 12: 自动扫描 Lib 目录并导入未在硬编码中注册的新工具"""
    lib_dir = os.path.dirname(os.path.abspath(__file__))
    lib_path = os.path.join(lib_dir, "Lib")
    if not os.path.exists(lib_path):
        return 0
    
    imported_count = 0
    # 排除基础模块和已硬编码的模块
    exclude_modules = {
        "__init__", "__pycache__", "base", "evolve_core",
        "add", "get_current_date", "get_everything_info", "search", "complex_search",
        "read_file", "write_file", "list_directory", "search_files", "run_command",
        "web_search", "web_fetch", "python_eval", "git_clone", "git_pull", "get_system_info",
        "grep", "get_time", "calculate", "manage_blacklist", "manage_approved",
        "get_dangerous_patterns", "create_tool", "count_lines", "download_file", "file_info",
        "create_directory", "delete_file", "run_python_script", "hello_world", "reverse_text",
        "get_weather", "start_evolution", "get_evolution_status", "cancel_evolution", "resume_evolution",
        "generate_population", "mutate_prompt", "crossover_variants", "generate_ab_pair",
        "analyze_prompt", "evaluate_variant", "explain_fitness", "register_fitness_function",
        "update_fitness_weights", "list_fitness_functions", "validate_variant", "check_safety",
        "add_safety_pattern", "record_metrics", "get_metrics_window", "check_evolution_trigger",
        "detect_anomalies"
    }
    
    for filename in os.listdir(lib_path):
        if filename.endswith(".py") and filename not in exclude_modules and not filename.startswith("_"):
            module_name = filename[:-3]
            try:
                importlib.import_module(f"Lib.{module_name}")
                imported_count += 1
            except ImportError:
                pass  # 忽略未注册的模块
    return imported_count


def register_all_tools():
    """
    注册所有工具到 MCP 服务器
    修复：移除自定义包装器，直接注册原函数，恢复标准 MCP 行为
    """
    # 执行自动扫描
    new_imports = _auto_scan_lib_tools()
    if new_imports > 0:
        print(f"\n  [AUTO-SCAN] 发现并导入 {new_imports} 个新工具模块")

    registered_count = 0
    failed_count = 0

    for name, tool_def in ToolRegistry.get_all().items():
        try:
            # 🐾 猫娘修复：直接传递原函数
            # FastMCP 会自动处理同步函数的异步包装
            mcp.add_tool(
                tool_def.func,
                name=tool_def.name,
                description=tool_def.description
            )
            registered_count += 1
        except Exception as e:
            failed_count += 1
            print(f"  [FAIL] {name}: {e}")

    print(f"\n  ✅ 注册成功：{registered_count} 个工具")
    if failed_count > 0:
        print(f"  ⚠️ 注册失败：{failed_count} 个工具")

    return registered_count, failed_count


def main():
    """主入口函数"""
    registered, failed = register_all_tools()
    total = registered + failed

    print(f"\n{'='*60}")
    print("Ent MCP Server Started")
    print(f"Address: 127.0.0.1:58000")
    print(f"Tools: {total} (Success: {registered}, Failed: {failed})")
    print(f"{'='*60}")

    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()