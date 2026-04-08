# 携程智能旅行助手 (Ctrip Intelligent Travel Assistant) 🚀

这是一个基于 **LangGraph** 和 **阿里云百炼 (DashScope)** 构建的高级智能旅行代理系统。它采用多代理协同架构（Multi-Agent Architecture），能够处理复杂的航班查询、酒店预订、租车及旅行推荐业务，并集成 RAG（检索增强生成）技术用于政策问答。

---

## 🏗 系统架构

本系统采用层级代理模式，通过一个“主助理”进行意图分发，将任务委托给具备专门工具权限的子助理：

*   **主助理 (Primary Assistant)**: 负责初步识别用户意图并分发到特定的业务流程。
*   **专门助手 (Specilized Assistants)**:
    *   **航班助手**: 负责修改、取消航班。
    *   **酒店助手**: 处理酒店预订与变更。
    *   **用车助手**: 管理租车服务。
    *   **旅行推荐助手**: 提供景点导览与推荐。
*   **知识检索 (RAG)**: 集成阿里云百炼 `text-embedding-v3` 模型，通过向量检索快速回答企业政策问题。

---

## 🛠 快速上手

### 1. 环境准备
确保你的系统已安装 Python 3.10+ 环境。

```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
.\venv\Scripts\activate
```

### 2. 安装依赖包
激活环境后，执行以下命令安装核心依赖（包括 LangChain, LangGraph, DashScope 等）：

```powershell
pip install -r requirements.txt
```

### 3. 配置环境变量
在项目根目录创建 .env 文件，并填入你的 API 密钥：

```env
# 阿里云百炼配置
OPENAI_API_KEY=your_dashscope_api_key
OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-max
EMBEDDING_MODEL=text-embedding-v3

# 搜索工具配置 (Tavily)
TAVILY_API_KEY=your_tavily_api_key
```

### 4. 启动系统

项目采用了模块化架构，源码位于 `trip_assistant` 文件夹内。为了让 Python 能够正确识别包路径，启动时必须指定 `PYTHONPATH`。

**Windows (PowerShell) 推荐命令：**
```powershell
# 1. 设置源码根路径
$env:PYTHONPATH = ".\trip_assistant"

# 2. 启动图形化流程测试脚本
python .\trip_assistant\graph_chat\第三个流程图.py
```

**或者一行命令启动：**
```powershell
$env:PYTHONPATH=".\trip_assistant"; python .\trip_assistant\graph_chat\第三个流程图.py
```

---


## 📁 项目结构

```text
travel_assistant/
├── trip_assistant/          # 源代码目录
│   ├── graph_chat/          # 状态图逻辑与各级助理定义
│   │   ├── assistant.py     # 主助理与 Prompt 定义
│   │   └── 第三个流程图.py    # 执行入口
│   ├── tools/               # 业务工具集 (航班、酒店、SQLite 操作)
│   └── travel2.sqlite       # 示例业务数据库
├── requirements.txt         # 依赖清单
└── .env                     # 环境变量配置文件
```

---

## 🛡 安全与规范
1. **数据审计**：所有数据库写操作（如修改航班、取消预订）前，系统都会触发中断逻辑并请求人工确认（Human-in-the-loop）。
2. **代码规范**：本项目严格遵循 Google 编程规范，代码包含详细的中文注释。
3. **API 安全**：严禁将 .env 文件提交至 Git 仓库，已在 .gitignore 中默认屏蔽。

---

> [!TIP]
> **提示**：运行脚本前请确保 `travel2.sqlite` 数据库存在，首次运行会自动调用 `init_db.py`（若脚本包含）初始化基础数据。相关数据库连接：[百度网盘 (提取码: 6ykw)](https://pan.baidu.com/s/1pU3Jo-np16I0ih00leQpwg?pwd=6ykw)，下载后请放置在 `trip_assistant` 文件夹下。
