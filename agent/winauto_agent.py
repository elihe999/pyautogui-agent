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


def open_app():
    from pywinauto.application import Application

    try:
        app = Application(backend="uia").start("notepad.exe")
        import time

        time.sleep(10)
    except Exception as e:
        print(f"打开应用时出现错误: {e}")
        return False
    return True


openApp = StructuredTool.from_function(
    func=open_app,
    name="OpenApp",
    description="useful for when you need to open an application on Windows system",
)


def keyboard_input(
    text: str,
):
    from pywinauto.application import Application
    from pywinauto.keyboard import send_keys

    hwnd = win32gui.GetForegroundWindow()
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    print(pid)
    Application().connect(process=pid)
    send_keys(text, with_spaces=True)

    return True


keyboardInput = StructuredTool.from_function(
    func=keyboard_input,
    name="KeyboardInput",
    description="useful for when you need to input text by keyboard",
)


class winAutoAgent:
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
示例输入：{{"action": "打开应用", "app": "记事本", "text": "需要输入的文本"}}

可用工具：
1. OpenApp - 打开Windows应用程序
2. KeyboardInput - 在当前活动窗口输入文本

执行规则：
1. 首先分析JSON指令，确定要执行的操作类型
2. 如果是打开应用操作，使用OpenApp工具
3. 如果是输入文本操作，使用KeyboardInput工具
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
    # agent = NLPParserAgent()
    # jsonStr = agent.parse_instruction("打开记事本并输入文字123")
    # if isinstance(jsonStr, list):
    #     # 变成字符串
    #     result = " \n ".join(str(item) for item in jsonStr)
    #     jsonStr = result
    # print(jsonStr)
    # agent = winAutoAgent()
    # agent.execute(jsonStr)
    pass
