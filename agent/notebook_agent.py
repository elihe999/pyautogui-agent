from langchain_ollama import ChatOllama
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.tools import StructuredTool
import win32gui
import win32process
import time

"""open notepad.exe"""
def open_notebook():
    """
    打开应用:打开记事本。
    
    Returns:
        bool: 是否成功打开（或已打开）记事本
    """
    try:
        import psutil
        processes = psutil.process_iter()
        for process in processes:
            process_name = process.name().lower()
            if process_name == "notepad.exe":
                return True
                
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        from pywinauto.application import Application
        Application(backend="uia").start("notepad.exe")
        print("成功启动记事本应用程序。")
        time.sleep(2) # 等待启动
        return True

    except Exception as e:
        print(f"打开记事本时出现错误: {e}")
        return False


openNotebook = StructuredTool.from_function(
    func=open_notebook,
    name="openNotebook",
    description="智能打开记事本工具。如果记事本已打开，会自动跳过启动步骤并返回True。这是打开记事本的首选工具。",
)

"""input text by keyboard"""
def keyboard_input(
    text: str,
):
    from pywinauto.application import Application
    from pywinauto.keyboard import send_keys
    print(f"输入文本: {text}")
    pid = None
    try:
        import psutil
        processes = psutil.process_iter()
        for process in processes:
            try:
                process_name = process.name().lower()
                if process_name == "notepad.exe":
                    pid = process.pid
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                print("记事本已打开")
                pass
    except Exception as e:
        print(f"检查记事本状态时出现错误: {e}")
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
    print(f"Foreground PID: {pid}")
    if pid is None:
        print("未检测到记事本进程")
        return False
    try:
        Application().connect(process=pid)
    except Exception as e:
        print(
            f"Warning: Could not connect to process {pid}: {e}. Trying to send keys anyway."
        )

    send_keys(text, with_spaces=True)

    return True


keyboardInput = StructuredTool.from_function(
    func=keyboard_input,
    name="keyboardInput",
    description="useful for when you need to input text by keyboard. Input text must be a single string.",
    args_schema={
        "text": {"type": "string", "description": "要输入的文本"}
    },
)

"""check notepad.exe is opened"""
def check_notepad_opened():
    """
    检查记事本是否已打开

    Returns:
        bool: 是否已打开记事本
    """
    try:
        import psutil
        processes = psutil.process_iter()
        for process in processes:
            try:
                process_name = process.name().lower()
                if process_name == "notepad.exe":
                    print("记事本已打开")
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                print("记事本已打开")
                pass
    except Exception as e:
        print(f"检查记事本状态时出现错误: {e}")
        return False

checkNotepadOpened = StructuredTool.from_function(
    func=check_notepad_opened,
    name="checkNotepadOpened",
    description="useful for when you need to check if notepad.exe is opened",
)


class NotebookAgent:
    def __init__(self):
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

        self.chat_history = []

        llm = ChatOllama(base_url="http://localhost:11434", model="qwen3:4b")
        prompt_chat_custom_1 = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
你是一个专业的 Windows 记事本(Notepad) 自动化 Agent。你的目标是根据用户指令高效、准确地操作记事本，你只需要管一种应用，即记事本。

核心原则：
1. **状态感知**：在执行任何操作前，**必须**回顾[对话历史] (Chat History)。如果历史记录显示某个步骤（如“打开记事本”）已经成功完成，**严禁**重复执行该步骤，直接进行下一步或结束任务。
2. **工具使用**：
   - `openNotebook`: 智能打开工具。如果记事本已在运行，它会直接返回成功。**优先使用此工具来确保记事本处于打开状态。**
   - `keyboardInput`: 需要开始输入文本时使用。
   - `checkNotepadOpened`: 检查记事本是否已打开。

3. **适时停止**：
   - 如果用户指令对应的操作已全部执行完毕，请直接回复“操作完成”或类似确认语，**不要**再调用任何工具。
   - 不要进行无意义的状态检查，相信工具的返回结果。

输入格式：JSON对象，包含操作指令信息
示例：{{"action": "输入文本123"}}

执行流程：
1. 分析用户指令和对话历史。
2. 检查是否需要执行操作（避免重复）。
3. 观察工具输出。
4. 如果任务完成，输出最终回答并结束。

以下是用户输入的内容：{content}
                   """,
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{content}"),
                # 添加，不然报错ValueError: Prompt missing required variables: {'agent_scratchpad'}
                # 等价于("placeholder", "{agent_scratchpad}")....("placeholder", "{其他...参数}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        tools = [openNotebook, keyboardInput, checkNotepadOpened]
        agent_custom_chat_1 = create_tool_calling_agent(
            llm=llm, tools=tools, prompt=prompt_chat_custom_1
        )
        self.agent_custom_chat_executor_1 = AgentExecutor(
            agent=agent_custom_chat_1,
            tools=tools,
            verbose=True,
            max_iterations=5,          # 限制最大迭代次数，防止死循环
            handle_parsing_errors=True # 自动处理解析错误
        )

    def execute(self, content: str):
        """
        执行指令。支持单个指令字符串或包含多个指令的JSON列表字符串。
        """
        import json
        
        # 尝试解析内容
        try:
            parsed = json.loads(content)
            # 如果不是列表，则包装成列表
            if not isinstance(parsed, list):
                parsed = [parsed]
            print(f"检测到指令列表，包含 {len(parsed)} 个步骤，开始逐个执行...")
            results = []
            for i, item in enumerate(parsed):
                # 只保留action字段
                item = {k: v for k, v in item.items() if k in ["action"]}
                # 将单个字典转换回 JSON 字符串供单步执行使用
                step_str = json.dumps(item, ensure_ascii=False)
                
                from langchain_core.messages import AIMessage
                result = self._execute_single_step(step_str)
                # chat history
                self.chat_history.append(AIMessage(content=result["output"]))
                results.append(result)
            return results
        except (json.JSONDecodeError, TypeError):
            # 如果解析失败，则按单个指令处理
            pass

    def _execute_single_step(self, content: str):
        print(f"正在执行指令: {content}")
        result = self.agent_custom_chat_executor_1.invoke(
            {"content": content, "chat_history": self.chat_history}
        )
        print(f"执行结果: {result}")
        return result


if __name__ == "__main__":
    # agent = NotebookAgent()
    # agent.execute(jsonStr)
    pass
