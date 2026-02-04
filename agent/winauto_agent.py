from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_community.llms import Ollama
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.tools import StructuredTool
import win32gui, win32process
import os
import json
import re
import asyncio
import time


def get_app_by_description(app: str) -> str:
    """
    获取对应的可执行文件名
    注意：具体的映射逻辑已移植到 NLPParserAgent，此处直接返回传入的 app 名称（预期为可执行文件名）

    Args:
        app: 应用程序的可执行文件名

    Returns:
        可执行文件名
    """
    return app.lower().strip()


def open_app(app: str = "记事本"):
    """
    打开指定的应用程序

    Args:
        app: 要打开的应用程序的自然语言描述

    Returns:
        bool: 是否成功打开应用程序
    """

    try:
        # 根据描述获取可执行文件名
        exe_name = get_app_by_description(app)

        if not exe_name:
            print(f"不支持打开的应用程序: {app}")
            return False

        asyncio.run(open_exec_by_name(exe_name))


        time.sleep(5)
        return True

    except Exception as e:
        print(f"打开应用时出现错误: {e}")
        return False


async def open_exec_by_name(exe_name: str):
    from pywinauto.application import Application

    type = "uia"
    match exe_name:
        case "services.msc":
            type = "process"
        case "diskmgmt.msc":
            type = "process"
        case "msinfo32.exe":
            type = "process"
        # case "notepad.exe":
        # case "calc.exe":
        # case "taskmgr.exe":
        # case "explorer.exe":
        case _:
            type = "uia"

    match type:
        case "uia":
            Application(backend="uia").start(exe_name)
            print(f"成功打开应用程序: {exe_name}")
        case "process":
            os.system("start " + exe_name)  # 使用start命令打开
            print(f"成功start应用: {exe_name}")


openApp = StructuredTool.from_function(
    func=open_app,
    name="OpenApp",
    description="useful for when you need to open an application on Windows system. "
    "Parameter: app (string) - 应用程序的可执行文件名 (e.g. notepad.exe, calc.exe)",
    args_schema={
        "app": {"type": "string", "description": "应用程序的可执行文件名"}
    },
)


def keyboard_input(
    text: str,
):
    from pywinauto.application import Application
    from pywinauto.keyboard import send_keys

    hwnd = win32gui.GetForegroundWindow()
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    print(f"Foreground PID: {pid}")
    try:
        Application().connect(process=pid)
    except Exception as e:
        print(f"Warning: Could not connect to process {pid}: {e}. Trying to send keys anyway.")
    
    send_keys(text, with_spaces=True)

    return True


keyboardInput = StructuredTool.from_function(
    func=keyboard_input,
    name="keyboardInput",
    description="useful for when you need to input text by keyboard",
)


class WinAutoAgent:
    def __init__(self):
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

        llm = ChatOllama(base_url="http://localhost:11434", model="qwen3:4b")
        prompt_chat_custom_1 = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
你是一个专业的电脑操作执行agent，专门处理JSON格式的操作指令。

输入格式：JSON对象，包含操作指令信息
示例输入：{{"action": "打开应用", "app": "notepad.exe", "text": "需要输入的文本"}}

可用工具：
1. OpenApp - 打开Windows应用程序，传入参数app为可执行文件名
2. keyboardInput - 在当前活动窗口输入文本

执行规则：
1. 首先分析JSON指令，确定要执行的操作类型
2. 如果是打开应用操作，使用OpenApp工具
3. 如果是输入文本操作，使用keyboardInput工具
4. 如果JSON包含复合操作，按顺序执行多个工具
5. 如果请求的操作不在工具支持范围内，明确告知用户不支持的操作类型
6. 执行完成后返回操作结果和状态

错误处理：
- 如果应用无法打开，返回错误信息
- 如果输入操作失败，返回错误信息
- 如果JSON格式不正确，提示正确的格式要求

请严格遵循JSON指令执行，不要添加额外的操作。

以下是用户输入的内容：{content}
                   /no_think """,
                ),
                ("human", "{content}"),
                # 添加，不然报错ValueError: Prompt missing required variables: {'agent_scratchpad'}
                # 等价于("placeholder", "{agent_scratchpad}")....("placeholder", "{其他...参数}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        tools = [openApp, keyboardInput]
        agent_custom_chat_1 = create_tool_calling_agent(
            llm=llm, tools=tools, prompt=prompt_chat_custom_1
        )
        self.agent_custom_chat_executor_1 = AgentExecutor(
            agent=agent_custom_chat_1,
            tools=tools,
        )

    def execute(self, content: str):
        print(f"{self.agent_custom_chat_executor_1.invoke({'content': content})}")


if __name__ == "__main__":
    pass
