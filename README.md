# pyautogui-agent

AI 驱动的 Windows 桌面自动化代理，将自然语言指令转换为可执行的 Windows UI 操作。

## 项目概述

本项目使用 LangChain 和 Ollama 解析自然语言命令，并通过 pywinauto, pyautogui 等自动化工具 执行 Windows UI 自动化任务。它可以根据简单的语音或文字指令打开应用程序、输入文本以及执行其他操作。

## 功能特性

- **自然语言解析**：将用户指令转换为结构化的自动化步骤
- **Windows UI 自动化**：打开应用程序、输入文本、与 Windows UI 元素交互
- **AI 驱动**：使用大语言模型（Ollama/qwen3）进行智能命令解释
- **工具化架构**：可扩展的工具系统，便于添加新的自动化功能

## 环境要求

- Windows 操作系统
- Python 3.8+
- 运行中的 Ollama 服务（需安装 qwen3 模型）
- 必需的 Python 包：
  - langchain-ollama
  - langchain-core
  - langchain-community
  - pywinauto
  - pywin32

### 额外功能

- **语音输入**：通过麦克风记录语音指令

(asr)[https://github.com/openai/whisper]
(asr-server)[https://github.com/ahmetoner/whisper-asr-webservice]

## 安装配置

```bash
# 安装依赖
pip install langchain-ollama langchain-core langchain-community pywinauto pywin32

# 启动 Ollama 服务
ollama serve

# 下载所需模型
ollama pull qwen3:4b
ollama pull qwen3:0.6b
```

## 使用方法

### 运行主程序

```bash
python main.py
```

### 运行单个代理

```bash
# 运行自然语言解析代理
python -m agent.nlp_parser_agent

# 运行 Windows 自动化代理
python -m agent.winauto_agent

# 运行任务管理模式检查器
python -m agent.task_manage
```

### 使用示例

```python
from agent import winAutoAgent, NLPParserAgent
from agent.task_manage import checkMode

# 检查任务模式
task = checkMode("帮我打开记事本并输入文字123")

# 解析指令
nlp_parser = NLPParserAgent()
parsed_steps = nlp_parser.parse_instruction("帮我打开记事本并输入文字123")

# 执行自动化
agent = winAutoAgent()
agent.execute(parsed_steps)
```

## 项目结构

```
pyautogui-agent/
├── main.py                    # 程序入口
├── agent/
│   ├── __init__.py            # 包导出
│   ├── winauto_agent.py       # Windows UI 自动化代理
│   ├── nlp_parser_agent.py    # 自然语言指令解析器
│   └── task_manage.py         # 任务模式检查器
├── AGENTS.md                  # 代理开发指南
└── README.md                  # 项目说明文件
```

## 可用工具

### OpenApp
打开 Windows 应用程序。

```python
open_app() -> bool
```

### KeyboardInput
向活动窗口发送键盘输入。

```python
keyboard_input(text: str) -> bool
```

## 配置说明

在代理文件中修改 Ollama 基础 URL 和模型设置：

```python
llm = ChatOllama(base_url="http://localhost:11434", model="qwen3:4b")
```

## 开发指南

### 代码风格检查

```bash
flake8 agent/ main.py --max-line-length=100
```

### 类型检查

```bash
mypy agent/ main.py
```

### 代码格式化

```bash
black --check agent/ main.py
```

## 许可证

Apache License 2.0