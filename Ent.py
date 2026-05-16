"""
MCP 服务器主入口
"""
import sys
import inspect
import os
import importlib
import re  # <--- 新增这一行，已修复
from typing import Optional

# 确保 stdout 使用 UTF-8 编码
if sys.stdout.encoding != 'utf-8':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1, closefd=False)

from mcp.server.fastmcp import FastMCP
from Lib.base.base import ToolRegistry

# ========== 基础工具导入 =========
from Lib.tools.add import add
from Lib.tools.get_current_date import get_current_date
from Lib.tools.get_everything_info import get_everything_info
from Lib.tools.search import search
from Lib.tools.complex_search import complex_search
from Lib.tools.read_file import read_file
from Lib.tools.write_file import write_file
from Lib.tools.list_directory import list_directory
from Lib.tools.search_files import search_files
from Lib.tools.run_command import run_command
from Lib.tools.web_search import web_search
from Lib.tools.web_fetch import web_fetch
from Lib.tools.python_eval import python_eval
from Lib.tools.git_clone import git_clone
from Lib.tools.git_pull import git_pull
from Lib.tools.get_system_info import get_system_info
from Lib.tools.grep import grep
from Lib.tools.get_time import get_time
from Lib.tools.calculate import calculate
from Lib.tools.manage_blacklist import manage_blacklist
from Lib.tools.manage_approved import manage_approved
from Lib.tools.get_dangerous_patterns import get_dangerous_patterns
from Lib.tools.create_tool import create_tool
from Lib.tools.count_lines import count_lines
from Lib.tools.download_file import download_file
from Lib.tools.file_info import file_info
from Lib.tools.create_directory import create_directory
from Lib.tools.delete_file import delete_file
from Lib.tools.run_python_script import run_python_script
from Lib.tools.hello_world import hello_world
from Lib.tools.reverse_text import reverse_text
from Lib.tools.get_weather import get_weather

# ========== Evolve-MCP 工具导入 ==========
from Lib.evolution.start_evolution import start_evolution
from Lib.evolution.get_evolution_status import get_evolution_status
from Lib.evolution.cancel_evolution import cancel_evolution
from Lib.evolution.resume_evolution import resume_evolution
from Lib.evolution.generate_population import generate_population
from Lib.evolution.mutate_prompt import mutate_prompt
from Lib.evolution.crossover_variants import crossover_variants
from Lib.evolution.generate_ab_pair import generate_ab_pair
from Lib.evolution.analyze_prompt import analyze_prompt
from Lib.evolution.evaluate_variant import evaluate_variant
from Lib.evolution.explain_fitness import explain_fitness
from Lib.evolution.register_fitness_function import register_fitness_function
from Lib.evolution.update_fitness_weights import update_fitness_weights
from Lib.evolution.list_fitness_functions import list_fitness_functions
from Lib.evolution.validate_variant import validate_variant
from Lib.evolution.check_safety import check_safety
from Lib.evolution.add_safety_pattern import add_safety_pattern
from Lib.evolution.record_metrics import record_metrics
from Lib.evolution.get_metrics_window import get_metrics_window
from Lib.evolution.check_evolution_trigger import check_evolution_trigger
from Lib.evolution.detect_anomalies import detect_anomalies
# ========================================

# 创建 FastMCP 实例
mcp = FastMCP(
    "Ent MCP Server",
    host="127.0.0.1",
    port=58001,
    stateless_http=True,
    json_response=True,
)

"""【猫娘修复】Issue 12: 自动扫描 Lib 子目录并导入未在硬编码中注册的新工具"""
def _auto_scan_lib_tools():
    """【猫娘修复】Issue 12: 自动扫描 Lib 子目录并导入未在硬编码中注册的新工具"""
    lib_dir = os.path.dirname(os.path.abspath(__file__))
    lib_path = os.path.join(lib_dir, "Lib")
    if not os.path.exists(lib_path):
        return 0
    
    imported_count = 0
    # 【猫娘修改】：去除所有排除项，所有工具均需要自动发现。
    exclude_modules = set()

    # 【猫娘修改】：增加一个"白名单"列表，用于记录成功导入的模块名。
    discovered_modules = []

    # 递归扫描子目录
    for root, dirs, files in os.walk(lib_path):
        # 忽略 __pycache__
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
            
        for filename in files:
            if filename.endswith(".py") and filename not in exclude_modules and not filename.startswith("_"):
                module_name = filename[:-3]
                # 获取相对路径作为模块名，例如 Lib.tools.add
                rel_path = os.path.relpath(root, lib_dir)
                package_path = rel_path.replace("\\", ".").replace("/", ".")
                # 【猫娘修复】修正模块名构造逻辑：package_path 已包含 Lib 前缀，无需重复拼接
                full_module_name = f"{package_path}.{module_name}"
                
                try:
                    # 【猫娘修改】：增加查重逻辑。
                    # 只有当模块不在内存 (sys.modules) 中时，才执行导入并计数。
                    # 这样就不会重复统计已经在文件顶部硬编码导入的工具了。
                    if full_module_name not in sys.modules:
                        importlib.import_module(full_module_name)
                        imported_count += 1
                        discovered_modules.append(full_module_name)  # 【猫娘修改】：记录成功导入的模块名到白名单
                except ImportError:
                    pass
                    
    # 【猫娘修改】：在函数末尾打印"白名单/黑名单"机制，输出所有成功导入的模块名。
    if discovered_modules:
        print(f"  [AUTO-SCAN-LOG] Whitelist of Discovered Modules ({len(discovered_modules)} modules):")
        # 【猫娘修改】：保持列表格式，并为每个模块添加编号。
        for idx, module in enumerate(discovered_modules, 1):
            print(f"      {idx}. {module}")
    else:
        print("  [AUTO-SCAN-LOG] No new modules discovered.")
        
    return imported_count



def get_hardcoded_modules(script_path):
    """【猫娘修改】：解析脚本自身，提取所有硬编码导入的模块路径。【修改时间】：2026-05-12 18:36:00。"""
    hardcoded = set()
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            f_content = f.read()
        pattern = r'from\s+(Lib\.\S+)\s+import'
        matches = re.findall(pattern, f_content)
        return set(matches)
    except Exception as e:
        print(f"[WARN] Failed to parse hardcoded modules: {e}")
        return set()

def register_all_tools():
    """【猫娘修改】：重构注册逻辑，支持硬编码与自动发现工具的分类统计显示。【修改时间】：2026-05-12 18:36:00。"""
    # 获取当前脚本路径以解析硬编码
    current_script_path = os.path.abspath(__file__)
    hardcoded_modules = get_hardcoded_modules(current_script_path)
    
    # 执行自动扫描
    new_imports = _auto_scan_lib_tools()
    if new_imports > 0:
        print(f"\n  [AUTO-SCAN] Discovered and imported {new_imports} new tool modules")

    registered_count = 0
    failed_count = 0

    for name, tool_def in ToolRegistry.get_all().items():
        try:
            mcp.add_tool(
                tool_def.func,
                name=tool_def.name,
                description=tool_def.description
            )
            registered_count += 1
        except Exception as e:
            failed_count += 1
            print(f"  [FAIL] {name}: {e}")

    # 【猫娘修改】：显示所有工具的导入来源（文件夹位置）与工具名称，并统计总数。
    # 分类显示：硬编码 vs 自动发现
    print("\n  [TOOL_LISTING] Tool Sources & Statistics:")
    
    hardcoded_tools = []
    auto_discovered_tools = []

    try:
        for name, tool_def in ToolRegistry.get_all().items():
            try:
                source_file = inspect.getsourcefile(tool_def.func)
                module = inspect.getmodule(tool_def.func)
                module_name = module.__name__ if module else "N/A"
                
                # 判断分类
                if module_name in hardcoded_modules:
                    hardcoded_tools.append((name, source_file))
                else:
                    auto_discovered_tools.append((name, source_file))
            except TypeError:
                # 内置工具或无法获取源码的情况
                hardcoded_tools.append((name, "<Built-in>"))

        # 打印硬编码工具
        print(f"\n  [HARDCODED] ({len(hardcoded_tools)} tools):")
        # 【猫娘修改】：为 [HARDCODED] 部分添加编号，保持列表格式。
        for idx, (t_name, t_source) in enumerate(hardcoded_tools, 1):
            print(f"    {idx}. [{t_name}] <- {t_source}")

        # 打印自动发现工具
        print(f"\n  [AUTO-DISCOVERED] ({len(auto_discovered_tools)} tools):")
        # 【猫娘修改】：为 [AUTO-DISCOVERED] 部分添加编号，保持列表格式。
        for idx, (t_name, t_source) in enumerate(auto_discovered_tools, 1):
            print(f"    {idx}. [{t_name}] <- {t_source}")
            
        print(f"\n  [STATISTICS] Total Imported Tools: {len(hardcoded_tools) + len(auto_discovered_tools)}")

    except Exception as e:
        print(f"  [ERROR] Failed to generate tool report: {e}")

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
