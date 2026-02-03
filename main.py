from agent import winAutoAgent, NLPParserAgent
from agent.task_manage import checkMode

if __name__ == "__main__":
    # 初始化
    task = checkMode("帮我打开记事本并输入文字123")
    print(task)
    nlp_parser = NLPParserAgent()
    str = nlp_parser.parse_instruction("帮我打开记事本并输入文字123")
    print(str)
    agent = winAutoAgent()
    agent.execute(str)
