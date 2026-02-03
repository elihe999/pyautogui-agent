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


class NLPParserAgent:
    def __init__(self):
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

        self.llm = ChatOllama(base_url="http://localhost:11434", model="qwen3:4b")

        self.prompt = ChatPromptTemplate.from_template(
            """你是一个专业的电脑操作指令解析器。请将用户的自然语言指令解析为一个JSON数组，每个数组项都是一个操作步骤。

输入要求：用户描述电脑操作的句子
输出要求：返回一个JSON数组，格式为 [{{"step": 1, "action": "操作描述"}}, {{"step": 2, "action": "操作描述"}}]

解析规则：
1. 将复合指令拆分为独立的操作步骤
2. 每个步骤应该是原子性的单一操作
3. 保持原指令的语义完整性
4. 使用中文描述操作步骤
5. 识别常见的电脑操作：打开应用、输入文字、点击按钮、浏览网页等

示例：
输入："帮我打开记事本输入123"
输出：[{{"step": 1, "action": "打开记事本"}}, {{"step": 2, "action": "输入文字123"}}]

输入："先打开浏览器访问百度然后搜索Python教程"
输出：[{{"step": 1, "action": "打开浏览器"}}, {{"step": 2, "action": "访问百度网站"}}, {{"step": 3, "action": "搜索Python教程"}}]

现在请解析以下指令：
{instruction}

请只返回JSON数组，不要包含任何其他文本。/no_think"""
        )

    def parse_instruction(self, instruction: str):
        try:
            # 创建对话链，将提示词与语言模型连接起来
            chain = self.prompt | self.llm

            # 调用链并生成回答，传入指令作为参数
            result = chain.invoke({"instruction": instruction})

            # 获取回答文本并清理 <think>...</think> 内容
            response_text = result.content or ""
            if type(response_text) != str:
                response_text = str(response_text)
            # 删除 <think> 标签及其中的内容（支持跨行和大小写）
            response_text = re.sub(
                r"<think\b[^>]*>.*?</think>",
                "",
                response_text,
                0,
                flags=re.DOTALL | re.IGNORECASE,
            )

            # 提取首个 JSON 数组（[...]）并返回其字符串表示，优先返回解析后的 JSON （保持中文）
            start = response_text.find("[")
            end = response_text.rfind("]") + 1
            if start != -1 and end != -1 and end > start:
                json_text = response_text[start:end].strip()
                try:
                    parsed = json.loads(json_text)
                    return json.dumps(parsed, ensure_ascii=False)
                except Exception:
                    # 如果无法解析为 JSON，返回提取的文本片段
                    return json_text

            # 若未找到数组，返回清理后的原始文本
            return response_text.strip()

        except Exception as e:
            print(f"解析过程中出现错误: {e}")
            return ""


if __name__ == "__main__":
    agent = NLPParserAgent()
    jsonStr = agent.parse_instruction("打开记事本并输入文字123")
    if isinstance(jsonStr, list):
        # 变成字符串
        result = " \n ".join(str(item) for item in jsonStr)
        jsonStr = result
    print(jsonStr)
    agent = winAutoAgent()
    agent.execute(jsonStr)
