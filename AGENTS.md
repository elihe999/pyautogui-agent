# AGENTS.md - pyautogui-agent Development Guidelines

## Project Overview
This is a Windows automation agent that uses LangChain for AI-powered desktop operations. The project converts natural language instructions into executable Windows UI actions using pywinauto.

## Build & Development Commands

### Running the Application
```bash
# Run the main entry point
python main.py

# Run individual agent modules directly
python -m agent.winauto_agent
python -m agent.nlp_parser_agent
python -m agent.task_manage
```

### Linting & Type Checking
```bash
# Run flake8 for style checking
flake8 agent/ main.py --max-line-length=100

# Run mypy for type checking
mypy agent/ main.py

# Run black for formatting check
black --check agent/ main.py
```

### Testing
```bash
# Run pytest on entire test suite (if tests exist)
pytest

# Run a single test file
pytest tests/test_winauto_agent.py

# Run a single test
pytest tests/test_winauto_agent.py::TestClass::test_method
```

## Code Style Guidelines

### Imports
- Place standard library imports at the top of files
- Group imports: standard library, third-party, local application
- Use lazy imports (inside functions) for heavy dependencies like pywinauto when needed
- Example:
  ```python
  import os
  import json
  
  from langchain_ollama import ChatOllama
  from langchain_core.tools import tool
  
  from agent.task_manage import checkMode
  ```

### Formatting
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use blank lines to separate logical sections within functions
- No trailing whitespace
- Add blank line at end of file

### Types & Type Hints
- Use type hints for function parameters and return values
- Prefer explicit types over `Any` when possible
- Example:
  ```python
  def keyboard_input(text: str) -> bool:
      ...
  ```

### Naming Conventions
- **Classes**: PascalCase (e.g., `winAutoAgent`, `NLPParserAgent`)
- **Functions**: snake_case (e.g., `open_app`, `check_mode`)
- **Variables**: snake_case (e.g., `parsed_steps`, `content`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_MODEL`)
- **Private methods**: prefix with underscore (e.g., `_internal_method`)

### Error Handling
- Use try/except blocks for operations that may fail
- Catch specific exceptions when possible
- Always provide meaningful error messages
- Example:
  ```python
  try:
      result = chain.invoke({"instruction": instruction})
      parsed_steps = json.loads(result.content)
      return parsed_steps
  except Exception as e:
      print(f"解析过程中出现错误: {e}")
      return ""
  ```
- Let unexpected errors propagate with tracebacks for debugging

### Class Structure
- Initialize AI models and tools in `__init__`
- Keep `execute` or `parse_instruction` methods as primary entry points
- Use structured tool definitions for LangChain tools:
  ```python
  openApp = StructuredTool.from_function(
      func=open_app,
      name="OpenApp",
      description="useful for when you need to open an application on Windows system",
  )
  ```

### Comments & Documentation
- Write comments in Chinese for user-facing messages (as per project convention)
- Use docstrings for class and function documentation
- Example:
  ```python
  def keyboard_input(text: str) -> bool:
      """Send keyboard input to the active window."""
      ...
  ```

### LangChain Integration
- Use `ChatOllama` with appropriate base_url and model settings
- Create prompt templates using `ChatPromptTemplate`
- Chain prompts with models using the `|` operator
- Include `/no_think` suffix in prompts for Ollama models to disable thinking mode

### Windows Automation Patterns
- Use `Application(backend="uia")` for modern Windows UI automation
- Get foreground window with `win32gui.GetForegroundWindow()`
- Get process ID with `win32process.GetWindowThreadProcessId(hwnd)`
- Use `pywinauto.keyboard.send_keys()` for text input

## File Organization
- Main logic in `agent/` package
- Public classes exported in `agent/__init__.py`
- Entry point in `main.py`
- Keep platform-specific code (Windows) isolated where possible

## Dependencies
Key libraries used:
- `langchain-ollama`, `langchain-core`, `langchain-community`
- `pywinauto` for Windows UI automation
- `pywin32` for Windows API access
