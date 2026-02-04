from typing import Optional, Dict, Any
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import uuid
import os

from langchain_ollama import ChatOllama
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.tools import StructuredTool


def _ensure_datetime(dt_str: str, tz_str: Optional[str] = None) -> datetime:
    """解析字符串为带时区的 datetime 对象，支持 ISO 格式或 'YYYY-MM-DD HH:MM' 类型的输入。

    Args:
        dt_str: 日期时间字符串
        tz_str: 时区字符串，例如 'Asia/Shanghai'。如果未提供则默认使用 UTC。
    Returns:
        带时区的 datetime 对象
    """
    if isinstance(dt_str, datetime):
        dt = dt_str
    else:
        try:
            # 尝试解析 ISO 格式
            dt = datetime.fromisoformat(dt_str)
        except Exception:
            # 兼容 'YYYY-MM-DD HH:MM' 形式
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")

    # 如果是无时区信息的时间，则应用 tz
    if dt.tzinfo is None:
        if tz_str:
            tz = pytz.timezone(tz_str)
        else:
            tz = pytz.UTC
        dt = tz.localize(dt)
    return dt


def create_ics_event(
    summary: str,
    dtstart: str,
    dtend: Optional[str] = None,
    tz: Optional[str] = "UTC",
    description: Optional[str] = "",
    location: Optional[str] = "",
    uid: Optional[str] = None,
) -> Calendar:
    """创建包含单个事件的 Calendar 对象。

    Args:
        summary: 事件标题
        dtstart: 开始时间，字符串或 datetime
        dtend: 结束时间，字符串或 datetime。如果为空则按开始时间 + 1 小时
        tz: 时区名称（pytz 支持）
        description: 事件描述
        location: 事件地点
        uid: 事件 UID（可选）

    Returns:
        icalendar.Calendar 对象
    """
    tz = tz or "UTC"
    start_dt = _ensure_datetime(dtstart, tz)
    if dtend:
        end_dt = _ensure_datetime(dtend, tz)
    else:
        end_dt = start_dt + timedelta(hours=1)

    cal = Calendar()
    cal.add("prodid", "-//pyautogui-agent Calendar//example.com//")
    cal.add("version", "2.0")

    event = Event()
    event.add("uid", uid or str(uuid.uuid4()))
    event.add("dtstamp", datetime.now(pytz.UTC))
    event.add("summary", summary)
    event.add("dtstart", start_dt)
    event.add("dtend", end_dt)
    if description:
        event.add("description", description)
    if location:
        event.add("location", location)

    cal.add_component(event)
    return cal


def write_calendar_to_file(cal: Calendar, filename: str = "meeting.ics") -> str:
    """将 Calendar 对象写入文件并返回文件路径"""
    with open(filename, "wb") as f:
        f.write(cal.to_ical())
    return os.path.abspath(filename)

def current_utc_time() -> str:
    """获取当前 UTC 时间的 ISO 格式字符串"""
    return datetime.now(pytz.UTC).isoformat()

currentUTC = StructuredTool.from_function(
    func=current_utc_time,
    name="currentUTC",
    description="获取当前 UTC 时间的 ISO 格式字符串",
)

# StructuredTool: createICS
def create_ics_tool(
    summary: str,
    dtstart: str,
    dtend: Optional[str] = None,
    tz: Optional[str] = "UTC",
    description: Optional[str] = "",
    location: Optional[str] = "",
    filename: Optional[str] = "meeting.ics",
) -> Dict[str, Any]:
    """工具函数：创建一个 ICS 文件并返回文件路径和一些元数据"""
    try:
        cal = create_ics_event(
            summary=summary,
            dtstart=dtstart,
            dtend=dtend,
            tz=tz,
            description=description,
            location=location,
        )
        path = write_calendar_to_file(cal, filename or "meeting.ics")
        return {"success": True, "path": path, "message": f"ICS 文件已生成：{path}"}
    except Exception as e:
        return {"success": False, "message": str(e)}


createICS = StructuredTool.from_function(
    func=create_ics_tool,
    name="createICS",
    description="创建一个 .ics 日历文件。参数包括 summary, dtstart, dtend, tz, description, location, filename",
    args_schema={
        "summary": {"type": "string", "description": "事件标题"},
        "dtstart": {
            "type": "string",
            "description": "开始时间，支持 ISO 格式或 'YYYY-MM-DD HH:MM'",
        },
        "dtend": {
            "type": "string",
            "description": "结束时间，支持 ISO 格式或 'YYYY-MM-DD HH:MM'",
        },
        "tz": {"type": "string", "description": "时区，例如 'Asia/Shanghai'"},
        "description": {"type": "string", "description": "事件描述"},
        "location": {"type": "string", "description": "事件地点"},
        "filename": {"type": "string", "description": "输出文件名，例如 'meeting.ics'"},
    },
)

def open_ics(filename: str = "meeting.ics"):
    import os
    os.popen(filename)
    
    return {"success": True, "message": f"{filename} 已打开"}

importIcs = StructuredTool.from_function(
    func=open_ics,
    name="openICS",
    description="打开并导入一个 .ics 文件。参数包括 filename",
    args_schema={
        "filename": {"type": "string", "description": "ICS 文件名，例如 'meeting.ics'"},
    },
)

# StructuredTool: readICS
from icalendar import Calendar as ICal


def read_ics_file(filename: str = "meeting.ics") -> Dict[str, Any]:
    """读取 .ics 文件并返回内含事件的简要信息"""
    try:
        with open(filename, "rb") as f:
            data = f.read()
        cal = ICal.from_ical(data)
        events = []
        for component in cal.walk():
            if component.name == "VEVENT":
                ev = {
                    "summary": str(component.get("summary")),
                    "dtstart": str(component.get("dtstart").dt),
                    "dtend": str(component.get("dtend").dt) if component.get("dtend") else None,
                    "description": str(component.get("description")) if component.get("description") else "",
                    "location": str(component.get("location")) if component.get("location") else "",
                    "uid": str(component.get("uid")) if component.get("uid") else "",
                }
                events.append(ev)
        return {"success": True, "events": events}
    except Exception as e:
        return {"success": False, "message": str(e)}


readICS = StructuredTool.from_function(
    func=read_ics_file,
    name="readICS",
    description="读取 .ics 文件并返回事件信息（summary, dtstart, dtend, description, location, uid）",
    args_schema={"filename": {"type": "string", "description": "要读取的 .ics 文件路径"}},
)


class CalendarAgent:
    """一个用于创建和读取 ICS 文件的小 Agent，接口仿照 NotebookAgent 的实现风格。"""

    def __init__(self):
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

        self.chat_history = []

        llm = ChatOllama(base_url="http://localhost:11434", model="qwen3:4b")

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
你是一个 Calendar Agent，可以理解自然语言或 JSON 指令，并负责创建或读取 .ics 日历文件。

可用工具：
- createICS(summary, dtstart, dtend, tz, description, location, filename) - 创建一个 .ics 日历文件。参数包括 summary, dtstart, dtend, tz, description, location, filename
- readICS(filename) - 读取 .ics 文件并返回事件信息（summary, dtstart, dtend, description, location, uid）
- currentUTC() - 获取当前 UTC 时间
- importIcs(filename) - 打开并导入一个 .ics 文件。参数包括 filename

行为规范：
1. 优先处理自然语言指令（例如：“下周五公司团建活动，下午2点到5点，在市中心公园举行，帮我导出为 meeting.ics”）。
2. 从自然语言中提取必要字段并调用对应工具；若缺少必要信息（例如未给出开始时间或标题），应向用户提问确认。
3. 当用户请求“查看/读取/列出（某个 .ics 文件）”时，调用 readICS 工具。
4. 如果没有提供 filename，则默认使用 "meeting.ics"。
5. 操作完成后，返回简洁的确认信息（中文），包含 success 状态和生成文件路径或读取到的事件摘要；若发生错误，返回错误信息并提示下一步动作。

示例自然语言输入：
- “下周五公司团建活动，下午2点到5点，在市中心公园举行，帮我导出为 meeting.ics。”
- “读取 test_meeting.ics 并列出事件。”

如果用户以 JSON 形式输入（advanced 模式），也应兼容处理。
                    """,
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{content}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        tools = [createICS, readICS, currentUTC, importIcs]
        agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
        self.executor = AgentExecutor(
            agent=agent, tools=tools, verbose=True, max_iterations=5, handle_parsing_errors=True
        )

    def execute(self, content: Optional[str] = None):
        """执行指令，优先将自然语言直接传给 agent（也支持 JSON 输入）。

        如果未传入 content，会返回错误信息而不是抛出 TypeError，方便外部调用时排查问题。
        """
        if content is None:
            return {"success": False, "message": "缺少参数: content。请提供自然语言指令或 JSON 字符串。"}

        from json import JSONDecodeError
        import json

        # 如果是 JSON 格式，按原有批量执行流程处理
        try:
            parsed = json.loads(content)
            if not isinstance(parsed, list):
                parsed = [parsed]
            results = []
            for item in parsed:
                step_str = json.dumps(item, ensure_ascii=False)
                from langchain_core.messages import AIMessage
                result = self._execute_single_step(step_str)
                # 将 agent 输出保存到 chat_history（如果存在）
                try:
                    self.chat_history.append(AIMessage(content=result.get("output", "")))
                except Exception:
                    pass
                results.append(result)
            return results
        except (JSONDecodeError, TypeError):
            # 自然语言路径：直接交给 agent 处理，并将输出保存到 chat_history
            result = self._execute_single_step(content)
            try:
                from langchain_core.messages import AIMessage
                self.chat_history.append(AIMessage(content=result.get("output", "")))
            except Exception:
                pass
            return result

    def _execute_single_step(self, content: str):
        print(f"执行指令: {content}")
        result = self.executor.invoke({"content": content, "chat_history": self.chat_history})
        print(f"执行结果: {result}")
        return result


if __name__ == "__main__":
    # 简单示例
    agent = CalendarAgent()
    # 创建一个示例事件
    instruction = '下周五公司团建活动，下午2点到5点，在市中心公园举行，导入到日历中。'
    print(agent.execute(instruction))
