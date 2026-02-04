# pyautogui-agent

AI-powered Windows desktop automation agent that converts natural language instructions into executable Windows UI actions.

## Overview

This project uses LangChain with Ollama to parse natural language commands and execute Windows UI automation tasks using pywinauto, pyautogui. It can open applications, input text, and perform other operations based on simple voice or text instructions.

## Features

- **Natural Language Parsing**: Convert user instructions into structured automation steps
- **Windows UI Automation**: Open applications, input text, and interact with Windows UI elements
- **AI-Powered**: Uses LLM (Ollama/qwen3) for intelligent command interpretation
- **Tool-Based Architecture**: Extensible tool system for adding new automation capabilities

## Requirements

- Windows OS
- Python 3.8+
- Ollama server running with qwen3 model
- Required packages:
  - langchain-ollama
  - langchain-core
  - langchain-community
  - pywinauto
  - pywin32

## Installation

```bash
# Install dependencies
pip install langchain-ollama langchain-core langchain-community pywinauto pywin32

# Start Ollama server
ollama serve

# Pull required model
ollama pull qwen3:4b
ollama pull qwen3:0.6b
```

## Usage

### Run the main application

```bash
python main.py
```

### Test individual agents

```bash
# Run NLP parser agent
python -m agent.nlp_parser_agent

# Run Windows automation agent
python -m agent.winauto_agent

# Run task management mode checker
python -m agent.task_manage
```

### Example

```python
from agent import winAutoAgent, NLPParserAgent
from agent.task_manage import checkMode

# Check task mode
task = checkMode("帮我打开记事本并输入文字123")

# Parse instruction
nlp_parser = NLPParserAgent()
parsed_steps = nlp_parser.parse_instruction("帮我打开记事本并输入文字123")

# Execute automation
agent = winAutoAgent()
agent.execute(parsed_steps)
```

## Project Structure

```
pyautogui-agent/
├── main.py                    # Entry point
├── agent/
│   ├── __init__.py            # Package exports
│   ├── winauto_agent.py       # Windows UI automation agent
│   ├── nlp_parser_agent.py    # Natural language instruction parser
│   └── task_manage.py         # Task mode checker
├── AGENTS.md                  # Development guidelines for agents
└── README.md                  # This file
```

## Available Tools

### OpenApp

Opens a Windows application.

```python
open_app() -> bool
```

### KeyboardInput

Sends keyboard input to the active window.

```python
keyboard_input(text: str) -> bool
```

## Configuration

Modify the Ollama base URL and model settings in the agent files:

```python
llm = ChatOllama(base_url="http://localhost:11434", model="qwen3:4b")
```

## License

Apache License 2.0
