# Ent MCP Server

> 基于 MCP (Model Context Protocol) 的全功能 AI 辅助开发服务器

---

## 📁 项目概览

| 项目 | 信息 |
|------|------|
| **名称** | Ent MCP Server |
| **版本** | 0.3.0 |
| **入口文件** | `Ent.py` |
| **运行地址** | `127.0.0.1:58000` |
| **协议** | streamable-http |
| **Python 版本** | >=3.10 |
| **总工具数** | 76 个（基础 34 + 番茄 6 + 网易云 13 + 进化 21 + PDF 2） |

---


## 🗂 目录结构

```
E:\Codes\AI Related\MCP Server\
├── Ent.py                          # 主入口：MCP 服务器初始化与工具注册
├── pyproject.toml                  # Python 项目配置（依赖与构建）
├── requirements.txt                # 依赖清单（手动管理）
├── .python-version                 # Python 版本锁定：3.10
├── .gitignore                      # Git 忽略规则
├── evolve-mcp 重写说明.md          # evolve-mcp 功能重写文档
├── README.md                       # 项目说明文档（本文件）
├── Lib/                            # 工具模块目录（重构后）
│   ├── __init__.py                 # 初始化
│   ├── base/                       # 基础架构模块
│   │   ├── __init__.py
│   │   └── base.py                 # 基础工具装饰器、缓存机制、注册表
│   ├── evolution/                  # 进化引擎模块
│   │   ├── __init__.py
│   │   ├── evolve_core.py          # 进化核心：变异生成器、适应度评估、安全验证、指标收集
│   │   └── evolution_state.json    # 进化状态持久化文件（JSON 增量索引）
│   ├── fanqie/                     # 番茄小说工具
│   │   ├── __init__.py
│   │   ├── fanqie_api.py           # 番茄小说：核心 API 交互
│   │   ├── fanqie_book.py          # 番茄小说：书籍信息获取
│   │   ├── fanqie_config.py        # 番茄小说：配置管理
│   │   ├── fanqie_content.py       # 番茄小说：内容获取与解析
│   │   ├── fanqie_misc.py          # 番茄小说：杂项功能
│   │   └── fanqie_search.py        # 番茄小说：搜索功能
│   ├── netease/                    # 网易云音乐工具
│   │   ├── __init__.py
│   │   ├── netease_config.py       # 网易云音乐：配置与控制器状态
│   │   ├── netease_control.py      # 网易云音乐：基础控制（播放/音量/快捷键）
│   │   ├── netease_daily.py        # 网易云音乐：每日推荐与私人漫游（Selenium）
│   │   ├── netease_playlist.py     # 网易云音乐：歌单管理
│   │   └── netease_search.py       # 网易云音乐：搜索与播放
│   ├── pdf_reader/                 # PDF 阅读器工具（猫娘新增）
│   │   ├── __init__.py
│   │   ├── pdf_read_local.py       # PDF 阅读器：本地文件读取
│   │   └── pdf_read_url.py         # PDF 阅读器：URL 内容获取
│   └── tools/                      # 通用工具集
│       ├── __init__.py
│       ├── add.py                  # 基础数学
│       ├── calculate.py            # 数学表达式计算
│       ├── count_lines.py          # 统计代码行数
│       ├── create_directory.py     # 创建目录
│       ├── create_tool.py          # 动态创建 MCP 工具
│       ├── delete_file.py          # 删除文件
│       ├── download_file.py        # 下载文件
│       ├── file_info.py            # 获取文件元数据
│       ├── get_current_date.py     # 获取当前日期
│       ├── get_dangerous_patterns.py # 获取危险命令模式
│       ├── get_everything_info.py  # 获取 Everything 状态信息
│       ├── get_system_info.py      # 获取系统信息
│       ├── get_time.py             # 获取当前时间
│       ├── get_weather.py          # 获取城市天气
│       ├── git_clone.py            # 克隆 Git 仓库
│       ├── git_pull.py             # 拉取远程更新
│       ├── grep.py                 # 文本模式搜索
│       ├── hello_world.py          # 问候语示例
│       ├── list_directory.py       # 列出目录内容
│       ├── manage_approved.py      # 管理已批准命令
│       ├── manage_blacklist.py     # 管理命令黑名单
│       ├── python_eval.py          # 执行 Python 代码片段
│       ├── read_file.py            # 读取文件内容
│       ├── run_command.py          # 执行 Shell 命令
│       ├── run_python_script.py    # 执行 Python 脚本
│       ├── search.py               # Everything 搜索引擎
│       ├── complex_search.py       # 复杂组合搜索
│       ├── search_files.py         # 通配符搜索文件
│       ├── web_fetch.py            # 抓取网页内容
│       ├── web_search.py           # 网络搜索
│       ├── write_file.py           # 写入文件内容
│       └── reverse_text.py         # 字符串反转
└── __pycache__/                    # Python 字节码缓存（自动）
```


## 🔧 核心模块

### Ent.py — MCP 服务器主入口

| 属性 | 值 |
|------|-----|
| **类型** | 入口文件 |
| **功能** | 服务器初始化、工具扫描与注册、启动服务 |
| **关键组件** | FastMCP 实例、ToolRegistry、自动扫描机制 |
| **端口** | 58000 |
| **传输协议** | streamable-http |

**核心逻辑：**
1. 创建 FastMCP 实例（host: 127.0.0.1, port: 58000）
2. 硬编码导入核心工具模块
3. `_auto_scan_lib_tools()`：自动扫描 Lib 目录发现新工具（如新增的 PDF Reader、Fanqie、Netease 模块）
4. `register_all_tools()`：遍历 ToolRegistry 注册所有工具
5. `main()`：启动 MCP 服务

---

### Lib/base.py — 基础工具框架

| 属性 | 值 |
|------|-----|
| **类型** | 基础架构模块 |
| **功能** | 工具装饰器、LRU 缓存机制、工具注册表 |
| **核心类** | `ToolDefinition`, `ToolRegistry` |
| **核心函数** | `tool()`, `cache()`, `clear_cache()` |

**关键特性：**
- `@tool(name, description, schema)`：工具注册装饰器，自动从函数签名生成 JSON Schema
- `@cache(ttl, max_size)`：LRU 缓存装饰器，支持 TTL 与容量淘汰
- `ToolRegistry`：全局工具注册表，支持增删查操作
- `_infer_schema(func)`：自动从 Python 类型注解推断 JSON Schema

---

### Lib/pdf_reader — PDF 阅读器模块

| 属性 | 值 |
|------|-----|
| **类型** | 文件解析模块 |
| **功能** | 本地/URL PDF 内容提取 |
| **依赖** | PyPDF2 |

**核心工具：**
- `pdf_read_local`: 从本地路径读取 PDF 文本。
- `pdf_read_url`: 从 URL 下载并读取 PDF 文本。

---

## 📦 基础工具集（34 个）

### 🖥 文件操作

| 工具名 | 文件路径 | 功能描述 |
|--------|----------|----------|
| `read_file` | `Lib/read_file.py` | 读取文件内容 |
| `write_file` | `Lib/write_file.py` | 写入文件内容 |
| `list_directory` | `Lib/list_directory.py` | 列出目录内容 |
| `search_files` | `Lib/search_files.py` | 通配符搜索文件 |
| `create_directory` | `Lib/create_directory.py` | 创建目录 |
| `delete_file` | `Lib/delete_file.py` | 删除文件 |
| `file_info` | `Lib/file_info.py` | 获取文件元数据 |
| `count_lines` | `Lib/count_lines.py` | 统计代码行数（按扩展名） |

### 🔍 搜索工具

| 工具名 | 文件路径 | 功能描述 |
|--------|----------|----------|
| `search` | `Lib/search.py` | Everything 搜索引擎（支持正则、路径匹配等） |
| `complex_search` | `Lib/complex_search.py` | 复杂组合搜索 |
| `get_everything_info` | `Lib/get_everything_info.py` | 获取 Everything 状态信息 |
| `grep` | `Lib/grep.py` | 文本模式搜索 |
| `web_search` | `Lib/web_search.py` | 网络搜索（DDG 引擎） |
| `web_fetch` | `Lib/web_fetch.py` | 抓取网页内容 |

### 💻 命令执行

| 工具名 | 文件路径 | 功能描述 |
|--------|----------|----------|
| `run_command` | `Lib/run_command.py` | 执行 Shell 命令 |
| `run_python_script` | `Lib/run_python_script.py` | 执行 Python 脚本 |
| `python_eval` | `Lib/python_eval.py` | 执行 Python 代码片段（线程隔离） |
| `calculate` | `Lib/calculate.py` | 数学表达式计算 |
| `add` | `Lib/add.py` | 两数相加 |

### 🌐 网络与系统

| 工具名 | 文件路径 | 功能描述 |
|--------|----------|----------|
| `get_weather` | `Lib/get_weather.py` | 获取城市天气 |
| `download_file` | `Lib/download_file.py` | 下载文件 |
| `git_clone` | `Lib/git_clone.py` | 克隆 Git 仓库 |
| `git_pull` | `Lib/git_pull.py` | 拉取远程更新 |
| `get_system_info` | `Lib/get_system_info.py` | 获取系统信息 |
| `get_time` | `Lib/get_time.py` | 获取当前时间 |
| `get_current_date` | `Lib/get_current_date.py` | 获取当前日期 |

### 🛠 工具管理

| 工具名 | 文件路径 | 功能描述 |
|--------|----------|----------|
| `create_tool` | `Lib/create_tool.py` | 动态创建 MCP 工具 |
| `manage_blacklist` | `Lib/manage_blacklist.py` | 管理命令黑名单 |
| `manage_approved` | `Lib/manage_approved.py` | 管理已批准命令 |
| `get_dangerous_patterns` | `Lib/get_dangerous_patterns.py` | 获取危险命令模式 |

### 🎯 辅助工具

| 工具名 | 文件路径 | 功能描述 |
|--------|----------|----------|
| `hello_world` | `Lib/hello_world.py` | 问候语示例 |
| `reverse_text` | `Lib/reverse_text.py` | 字符串反转 |

---

## 📄 PDF 阅读器工具集（2 个）

### 📚 内容提取

| 工具名 | 文件路径 | 功能描述 |
|--------|----------|----------|
| `pdf_read_local` | `Lib/pdf_reader/pdf_read_local.py` | 从本地文件系统读取 PDF 文本内容 |
| `pdf_read_url` | `Lib/pdf_reader/pdf_read_url.py` | 从 URL 下载 PDF 并提取文本内容 |

---

## 🍅 番茄小说工具集（6 个）

### 📚 书籍与内容

| 工具名 | 文件路径 | 功能描述 |
|--------|----------|----------|
| `fanqie_get_book_detail` | `Lib/fanqie_book.py` | 获取指定书籍的详细信息 |
| `fanqie_get_book_directory` | `Lib/fanqie_book.py` | 获取书籍的完整章节目录列表 |
| `fanqie_get_simple_directory` | `Lib/fanqie_book.py` | 获取书籍的简化目录信息 |
| `fanqie_get_chapter_content` | `Lib/fanqie_content.py` | 获取指定章节的文本内容（简化接口） |

### 🔎 搜索与内容获取

| 工具名 | 文件路径 | 功能描述 |
|--------|----------|----------|
| `fanqie_search_books` | `Lib/fanqie_search.py` | 搜索番茄小说平台上的书籍、听书、漫画或短剧 |
| `fanqie_get_content` | `Lib/fanqie_content.py` | 统一的内容获取接口，支持小说、听书、短剧、漫画及批量获取 |

---

## 🎵 网易云音乐控制器（13 个）

### 🎮 基础控制

| 工具名 | 文件路径 | 功能描述 |
|--------|----------|----------|
| `launch_netease_music` | `Lib/netease_control.py` | 启动网易云音乐应用，支持自动最小化 |
| `control_playback` | `Lib/netease_control.py` | 控制播放状态（播放/暂停、上/下一首） |
| `control_volume` | `Lib/netease_control.py` | 控制音量（增加/减少） |
| `toggle_mini_mode` | `Lib/netease_control.py` | 切换迷你/全屏模式 |
| `like_current_song` | `Lib/netease_control.py` | 喜欢当前歌曲 |
| `toggle_lyrics` | `Lib/netease_control.py` | 显示/隐藏歌词 |

### 🎼 搜索与播放

| 工具名 | 文件路径 | 功能描述 |
|--------|----------|----------|
| `search_and_play_song` | `Lib/netease_search.py` | 搜索歌曲并直接播放 |
| `search_and_play_playlist` | `Lib/netease_search.py` | 搜索歌单并直接播放 |

### 📋 歌单管理

| 工具名 | 文件路径 | 功能描述 |
|--------|----------|----------|
| `manage_custom_playlists` | `Lib/netease_playlist.py` | 管理自定义歌单（增、删、查） |

### 🌟 高级功能（Selenium 自动化）

| 工具名 | 文件路径 | 功能描述 |
|--------|----------|----------|
| `play_daily_recommend` | `Lib/netease_daily.py` | 播放每日推荐歌单 |
| `play_roaming` | `Lib/netease_daily.py` | 启动私人漫游功能 |

### ⚙️ 配置与状态

| 工具名 | 文件路径 | 功能描述 |
|--------|----------|----------|
| `get_netease_config` | `Lib/netease_config.py` | 获取网易云音乐配置与路径状态 |
| `get_controller_info` | `Lib/netease_config.py` | 获取控制器信息与功能列表 |

---

## 🧬 进化引擎工具集（21 个）

### 🔄 进化生命周期（4 个）

| 工具名 | 文件路径 | 功能描述 |
|--------|----------|----------|
| `start_evolution` | `Lib/start_evolution.py` | 启动进化周期（猫娘修改：触发后自动执行一代） |
| `get_evolution_status` | `Lib/get_evolution_status.py` | 获取进化周期状态 |
| `cancel_evolution` | `Lib/cancel_evolution.py` | 取消进化周期 |
| `resume_evolution` | `Lib/resume_evolution.py` | 从检查点恢复进化 |

### 🧪 变体生成（5 个）

| 工具名 | 文件路径 | 功能描述 |
|--------|----------|----------|
| `generate_population` | `Lib/generate_population.py` | 生成 Prompt 变体种群 |
| `mutate_prompt` | `Lib/mutate_prompt.py` | 变异单个 Prompt |
| `crossover_variants` | `Lib/crossover_variants.py` | 两个变体交叉生成后代 |
| `generate_ab_pair` | `Lib/generate_ab_pair.py` | 生成 A/B 测试对 |
| `analyze_prompt` | `Lib/analyze_prompt.py` | 分析 Prompt 复杂度 |

### 📊 适应度评估（5 个）

| 工具名 | 文件路径 | 功能描述 |
|--------|----------|----------|
| `evaluate_variant` | `Lib/evaluate_variant.py` | 评估变体适应度分数 |
| `explain_fitness` | `Lib/explain_fitness.py` | 解释适应度分解详情 |
| `register_fitness_function` | `Lib/register_fitness_function.py` | 注册自定义适应度函数 |
| `update_fitness_weights` | `Lib/update_fitness_weights.py` | 更新适应度权重 |
| `list_fitness_functions` | `Lib/list_fitness_functions.py` | 列出已注册的适应度函数 |

### 🛡 安全验证（3 个）

| 工具名 | 文件路径 | 功能描述 |
|--------|----------|----------|
| `validate_variant` | `Lib/validate_variant.py` | 验证变体安全性 |
| `check_safety` | `Lib/check_safety.py` | 检查文本安全性 |
| `add_safety_pattern` | `Lib/add_safety_pattern.py` | 添加自定义安全模式 |

### 📈 指标收集（4 个）

| 工具名 | 文件路径 | 功能描述 |
|--------|----------|----------|
| `record_metrics` | `Lib/record_metrics.py` | 记录任务指标数据 |
| `get_metrics_window` | `Lib/get_metrics_window.py` | 获取时间窗口聚合指标 |
| `check_evolution_trigger` | `Lib/check_evolution_trigger.py` | 检查是否触发进化 |
| `detect_anomalies` | `Lib/detect_anomalies.py` | 检测指标异常 |

---

## ⚙️ 配置文件

### pyproject.toml

| 字段 | 值 |
|------|-----|
| **name** | my-mcp-server |
| **version** | 0.1.0 |
| **requires-python** | >=3.10 |
| **核心依赖** | mcp, everytools, ddgs, httpx, selectolax, requests |
| **扩展依赖** | pyautogui, selenium, psutil, pywin32 (网易云模块), PyPDF2 (PDF 模块) |

### requirements.txt

| 类别 | 依赖 |
|------|------|
| 核心框架 | mcp |
| Everything 搜索 | everytools |
| Web 搜索 | ddgs |
| HTTP 客户端 | httpx |
| HTML 解析 | selectolax |
| 网络请求 | requests |
| 网易云基础 | pyautogui>=0.9.54, pywin32>=306 |
| 网易云自动化 | selenium>=4.0.0, psutil>=5.9.0 |
| PDF 解析 | PyPDF2>=3.0.0 |

### .gitignore

- Python 生成的文件：`__pycache__/`, `*.py[oc]`, `build/`, `dist/`, `*.egg-info`
- 虚拟环境：`.venv`

### .python-version

- Python 版本锁定：**3.10**

---

## 🚀 快速开始

```bash
# 进入项目目录
cd E:\Codes\AI Related\MCP Server

# 启动服务器
python Ent.py
```

**启动输出示例：**
```
============================================================
Ent MCP Server Started
Address: 127.0.0.1:58001
Tools: 76 (Success: 76, Failed: 0)
============================================================
```

---

## 📝 架构说明

### 工具注册机制

```
Ent.py (入口)
  ├── 硬编码导入所有工具模块
  ├── _auto_scan_lib_tools() → 自动发现新工具（如 PDF Reader/Fanqie/Netease 模块）
  └── register_all_tools() → 遍历 ToolRegistry 注册
       └── mcp.add_tool(func, name, description)
```

### 进化引擎流程

```
start_evolution() 触发
  └── EvolutionPipeline.run_generation()
       ├── Step 1: generate → 生成新种群
       ├── Step 2: evaluate → 评估适应度
       ├── Step 3: mutate → 变异优选个体
       └── Step 4: save → 持久化状态（JSON 增量索引）
```

### 安全策略

- 注入检测：Prompt 注入、命令注入、路径遍历
- 自定义模式：支持动态添加安全规则
- 资源限制：CPU、内存、超时阈值配置

---

## 📌 注意事项

1. **状态持久化**：进化状态存储于 `Lib/evolution_state.json`，使用 Schema v2 增量索引
2. **缓存机制**：LRU 缓存 TTL 为 3600 秒，最大 500 条
3. **内存限制**：Variant 缓存上限 5000 条，超过自动淘汰
4. **安全警告**：`run_command` 和 `python_eval` 涉及系统执行，请谨慎使用
5. **依赖安装**：确保安装 `requirements.txt` 中列出的所有依赖（特别是 `pyautogui`、`selenium` 和 `PyPDF2`）
6. **端口变更**：服务器端口已调整为 `58000`，请相应更新客户端配置

---

**最后更新**: 2026-05-12  
**项目维护**: 猫娘 (猫娘修改标注)
