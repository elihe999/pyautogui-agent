from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import json


class NLPParserAgent:
    def __init__(self):
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

        self.llm = ChatOllama(base_url="http://localhost:11434", model="qwen3:0.6b")

        self.prompt = ChatPromptTemplate.from_template(
            """你是一个专业的电脑操作指令解析器。请将用户的自然语言指令解析为一个JSON数组，每个数组项都是一个操作步骤。

输入要求：用户描述电脑操作的句子
输出要求：返回一个JSON数组，格式为 [{{"step": 1, "action": "操作类型", "app": "应用可执行文件名", "agent_type": "代理类型", "content": "其他内容"}}]

应用映射规则（请严格使用以下对应的可执行文件名作为app字段的值）：
- 记事本、notepad、笔记 -> notepad.exe
- 计算器、calc、计算 -> calc.exe
- 任务管理器、taskmgr -> taskmgr.exe
- 资源管理器、explorer -> explorer.exe
- 控制面板、control -> control.exe
- 注册表编辑器、regedit -> regedit.exe
- 服务、services -> services.msc
- 系统信息、msinfo32 -> msinfo32.exe
- 磁盘管理、disk、硬盘 -> diskmgmt.msc
- 如果未找到匹配应用，app字段请保持原样或为空字符串

代理类型(agent_type)判断规则：
- 如果 app 为 notepad.exe，则 agent_type 为 "notebook"
- 其他情况，agent_type 为 "default"

解析规则：
1. 将复合指令拆分为独立的操作步骤
2. 识别操作类型（如：打开应用、输入文本、点击按钮等）
3. 根据映射规则确定app字段的值
4. 根据app字段确定agent_type字段的值
5. 如果是输入文本，将文本内容放入content字段
6. 保持原指令的语义完整性

示例：
输入："帮我打开记事本输入123"
输出：[{{"step": 1, "action": "打开应用", "app": "notepad.exe", "agent_type": "notebook", "content": ""}}, {{"step": 2, "action": "输入文本", "app": "notepad.exe", "agent_type": "notebook", "content": "123"}}]

输入："启动计算器"
输出：[{{"step": 1, "action": "打开应用", "app": "calc.exe", "agent_type": "default", "content": ""}}]

现在请解析以下指令：
{instruction}

请只返回JSON数组，不要包含任何其他文本。"""
        )

    def parse_instruction(self, instruction: str):
        try:
            # 创建对话链，将提示词与语言模型连接起来
            chain = self.prompt | self.llm

            # 调用链并生成回答，传入指令作为参数
            result = chain.invoke({"instruction": instruction})

            # 提取并解析JSON内容
            response_text = result.content

            # 尝试解析JSON
            parsed_steps = json.loads(response_text)

            return parsed_steps

        except Exception as e:
            print(f"解析过程中出现错误: {e}")
            return ""


# 使用示例
if __name__ == "__main__":
    parser = NLPParserAgent()

    # 测试示例
    test_instructions = [
        "帮我打开记事本输入123",
        "先打开浏览器访问百度然后搜索Python教程",
        "打开Word文档写一段工作报告",
        "启动计算器并进行一些数学运算",
    ]

    for instruction in test_instructions:
        print(f"\n输入: {instruction}")
        steps = parser.parse_instruction(instruction)
        print("解析结果:")
        for step in steps:
            print(f"  步骤 {step['step']}: Action={step['action']}, App={step.get('app', 'N/A')}, AgentType={step.get('agent_type', 'N/A')}, Content={step.get('content', '')}")
