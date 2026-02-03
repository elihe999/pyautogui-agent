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
            print(f"  步骤 {step['step']}: {step['action']}")
