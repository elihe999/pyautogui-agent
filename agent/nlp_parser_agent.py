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
输出要求：返回一个JSON数组，格式为 [{{"step": 1, "action": "具体的动作描述（包含参数）", "app": "应用可执行文件名", "agent_type": "代理类型"}}]

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
- 如果动作是连续的，例如"打开记事本输入123"，即使现在是下一步‘输入123’， agent_type 依然为 "notebook"，因为要根据上文判断。

解析规则：
1. **完整性检查（CRITICAL）**：必须确保所有步骤的内容组合起来能覆盖原始指令的全部语义。不要丢失任何数字、文本或参数。例如"输入123"，"123"必须包含在action字段中。
2. **动作合并**：将动作与内容合并在`action`字段中。例如`action`应该是"输入文本123"，而不是简单的"输入文本"。
3. 识别操作类型（如：打开应用、输入文本、点击按钮等）。
4. 根据映射规则确定app字段的值。
5. 根据app字段确定agent_type字段的值。
6. 只有step, action, app, agent_type字段。

示例：
输入："帮我打开记事本输入123"
输出：[{{"step": 1, "action": "打开应用", "app": "notepad.exe", "agent_type": "notebook"}}, {{"step": 2, "action": "输入文本123", "app": "notepad.exe", "agent_type": "notebook"}}]

输入："启动计算器"
输出：[{{"step": 1, "action": "打开应用", "app": "calc.exe", "agent_type": "default"}}]

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
            print(
                f"  步骤 {step['step']}: Action={step['action']}, App={step.get('app', 'N/A')}, AgentType={step.get('agent_type', 'N/A')}"
            )
