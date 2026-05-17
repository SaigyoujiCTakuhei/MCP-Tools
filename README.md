# KazeMiMiRin的MCP工具集 v04

> 基于 MCP (Model Context Protocol) 的全功能 AI 辅助开发服务器
---

## 📁 项目概览

| 项目 | 信息 |
|------|------|
| **名称** | KazeMiMiRin的MCP工具集 |
| **版本** | 0.4.0 |
| **入口文件** | `Ent.py` |
| **运行地址** | `127.0.0.1:58001` |
| **协议** | streamable-http |
| **Python 版本** | >=3.10 |
| **总工具数** | 70+ 个（含基础、进化、PDF、网易云、思考引擎、提示词管理等） |

---

## 🗂 目录结构

```
E:\Codes\AI Related\MCP Server\v04（正在使用的版本）\
├── Ent.py                          # 主入口：MCP 服务器初始化与工具注册
├── pyproject.toml                  # Python 项目配置（依赖与构建）
├── requirements.txt                # 依赖清单
├── 版本说明.txt                     # 版本说明
├── evolve-mcp 重写说明.md          # evolve-mcp 功能重写文档
├── README.md                       # 项目说明文档（本文件）
├── .python-version                 # Python 版本锁定：3.10
├── .gitignore                      # Git 忽略规则
├── Lib/                            # 工具模块目录（重构后）
│   ├── __init__.py                 # 初始化
│   ├── base/                       # 基础架构模块
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   └── base.py                 # 基础工具装饰器、缓存机制、注册表
│   ├── evolution/                  # 进化引擎模块 (22 MCP 工具)
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   ├── add_safety_pattern.py
│   │   ├── analyze_prompt.py
│   │   ├── cancel_evolution.py
│   │   ├── check_evolution_trigger.py
│   │   ├── check_safety.py
│   │   ├── crossover_variants.py
│   │   ├── detect_anomalies.py
│   │   ├── evaluate_variant.py
│   │   ├── evolution_state.json    # 进化状态持久化 (Schema v2)
│   │   ├── evolve_core.py          # 进化核心：流水线调度与状态管理
│   │   ├── explain_fitness.py
│   │   ├── generate_ab_pair.py
│   │   ├── generate_population.py
│   │   ├── get_evolution_status.py
│   │   ├── get_metrics_window.py
│   │   ├── list_fitness_functions.py
│   │   ├── mutate_prompt.py
│   │   ├── record_metrics.py
│   │   ├── register_fitness_function.py
│   │   ├── resume_evolution.py
│   │   ├── start_evolution.py
│   │   ├── update_fitness_weights.py
│   │   └── validate_variant.py
│   ├── fanqie/                     # 番茄小说工具
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   ├── fanqie_api.py
│   │   ├── fanqie_book.py
│   │   ├── fanqie_config.py
│   │   ├── fanqie_content.py
│   │   ├── fanqie_misc.py
│   │   └── fanqie_search.py
│   ├── netease/                    # 网易云音乐工具
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   ├── netease_config.py
│   │   ├── netease_control.py
│   │   ├── netease_daily.py        # Selenium 自动化模块
│   │   ├── netease_playlist.py
│   │   └── netease_search.py
│   ├── pdf_reader/                 # PDF 阅读器工具
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   ├── pdf_read_local.py
│   │   └── pdf_read_url.py
│   ├── prompts/                    # 提示词管理与模板模块
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   ├── create_prompt_template.txt
│   │   ├── prompt_registry.py
│   │   └── refactor_mcp_project.txt
│   ├── sequential_thinking/        # 深度思考引擎模块
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   ├── config.py
│   │   ├── thinking_core.py
│   │   └── tool_register.py
│   └── tools/                      # 通用工具集 (32 MCP 工具)
│       ├── __init__.py
│       ├── __pycache__/
│       ├── add.py
│       ├── calculate.py
│       ├── complex_search.py
│       ├── count_lines.py
│       ├── create_directory.py
│       ├── create_tool.py
│       ├── delete_file.py
│       ├── download_file.py
│       ├── file_info.py
│       ├── get_current_date.py
│       ├── get_dangerous_patterns.py
│       ├── get_everything_info.py
│       ├── get_system_info.py
│       ├── get_time.py
│       ├── get_weather.py
│       ├── git_clone.py
│       ├── git_pull.py
│       ├── grep.py
│       ├── hello_world.py
│       ├── list_directory.py
│       ├── manage_approved.py
│       ├── manage_blacklist.py
│       ├── python_eval.py
│       ├── read_file.py
│       ├── reverse_text.py
│       ├── run_command.py
│       ├── run_python_script.py
│       ├── search.py
│       ├── search_files.py
│       ├── web_fetch.py
│       ├── web_search.py
│       └── write_file.py
└── __pycache__/                    # Python 字节码缓存（自动）
```

---

## 🔧 核心模块

### Ent.py — MCP 服务器主入口

| 属性 | 值 |
|------|-----|
| **类型** | 入口文件 |
| **功能** | 服务器初始化、工具扫描与注册、启动服务 |
| **关键组件** | FastMCP 实例、ToolRegistry、自动扫描机制 (`_auto_scan_lib_tools`) |
| **端口** | 58001 |
| **传输协议** | streamable-http |

**核心逻辑：**
1. 创建 FastMCP 实例（host: 127.0.0.1, port: 58001）
2. 硬编码导入核心工具模块
3. `_auto_scan_lib_tools()`：递归扫描 Lib 目录，自动发现并导入新工具（如 PDF, Netease, Fanqie, Prompts）
4. `register_all_tools()`：遍历 ToolRegistry 注册所有工具
5. `main()`：启动 MCP 服务
6. 所有`__init__.py`保持为空。

---

### 🧬 进化引擎 (Evolution Engine)

*   **核心**：`Lib/evolution/evolve_core.py`
*   **功能**：Prompt 变体生成、适应度评估、安全沙箱、指标追踪。
*   **特性**：
    *   Schema v2 增量索引策略（持久化优化）。
    *   自动流水线：`generate -> evaluate -> mutate -> save`。
    *   安全验证：内置注入检测与自定义规则。
    *   **22 个 MCP 工具**：涵盖从生成、变异、交叉到安全验证的全生命周期。

### 🍅 番茄小说 (FanQie)

*   **功能**：书籍搜索、目录获取、内容解析。
*   **依赖**：`requests`, `selectolax`。

### 🎵 网易云音乐 (Netease)

*   **功能**：播放控制、每日推荐、私人漫游（Selenium）、歌单管理。
*   **依赖**：`selenium`, `pyautogui`, `psutil`。

### 📝 提示词管理 (Prompts)

*   **核心**：`Lib/prompts/prompt_registry.py`
*   **功能**：提示词模板管理、动态加载与注册。
*   **文件**：包含 `create_prompt_template.txt` 和 `refactor_mcp_project.txt` 等辅助文件。

---

## 🚀 快速开始

```bash
# 进入项目目录
cd E:\Codes\AI Related\MCP Server\v04（正在使用的版本）

# 安装依赖
pip install -r requirements.txt

# 启动服务器
python Ent.py
```

**启动输出示例：**
```
============================================================
KazeMiMiRin的MCP工具集 Started
Address: 127.0.0.1:58001
Tools: 70 (Success: 70, Failed: 0)
============================================================
```

---

## 📝 架构说明

### 工具注册机制
*   **硬编码导入**：`Ent.py` 显式导入常用工具。
*   **自动扫描**：`_auto_scan_lib_tools()` 发现 `Lib/` 下所有 `*.py` 工具并动态注册。
*   **分类统计**：支持区分“硬编码”与“自动发现”的工具来源。

### 状态持久化
*   **进化状态**：`Lib/evolution/evolution_state.json` (Schema v2)。
*   **缓存机制**：LRU 缓存 (TTL: 3600s, Max Size: 5000)。

---

## 📌 注意事项

1.  **端口配置**：`Ent.py` 中 `FastMCP` 实例化端口配置为 `58001`，实际运行以该配置为准。
2.  **依赖环境**：确保已安装 `Python 3.10+`。
3.  **系统依赖**：
    *   `pywin32` (Windows 系统必需)。
    *   `selenium` (需配置 ChromeDriver 路径或使用自动管理)。
4.  **文件数量说明**：`Lib/evolution/` 目录下包含 22 个暴露的 MCP 工具模块（含1个状态文件）。

---

## 🧹 架构整洁规范（最高优先级）

> **规则**：所有新增功能模块必须严格遵循 `Lib/` 目录下的分类规范，**严禁**将业务逻辑文件直接放置于项目根目录。
> **执行标准**：
> 1. 新建模块需先在 `Lib/` 下创建独立子目录（如 `Lib/模块名/`）。
> 2. 子目录内必须包含 `__init__.py` 及核心逻辑文件（如 `模块名_mcp.py`）。
> 3. 根目录仅保留入口文件 (`Ent.py`)、配置文件 (`pyproject.toml`, `.python-version`)、依赖清单 (`requirements.txt`) 及文档。
> 4. 每次交付前需核对 `README.md` 目录树，确保物理路径与文档索引 100% 一致。

---

## 🔄 协议对齐规范（强制）

> **规则**：新增模块必须严格使用项目标准 `@tool` 装饰器（源自 `Lib.base.base`）将函数注册至 `ToolRegistry`。
> **执行标准**：
> 1. **必须导入**：`from Lib.base.base import tool`
> 2. **必须装饰**：使用 `@tool(name="...", description="...", schema={...})` 声明函数。
> 3. **严禁使用**：现代 `mcp.server` 装饰器 (`@app.list_tools()`, `@app.call_tool()`)，该类装饰器会创建独立 Server 实例，导致 `_auto_scan_lib_tools()` 无法捕获工具。
> 4. **校验机制**：启动 `Ent.py` 时观察 `[AUTO-SCAN-LOG]` 输出，确认模块已入库；检查 `[AUTO-DISCOVERED]` 工具列表是否包含新增功能。
> 5. **返回值规范**：支持异步函数 (`async def`)，直接返回字符串、字典或列表，由 `ToolRegistry` 统一封装处理。

---

**最后更新**: 2026-05-14  
**项目维护**: 风见魅铃的猫娘