from agent import winAutoAgent, NLPParserAgent
from agent.task_manage import checkMode

if __name__ == "__main__":
    # 测试不同的应用程序
    test_commands = [
        # "帮我打开记事本并输入文字123",
        # "打开计算器",
        "启动硬盘管理"
    ]
    
    nlp_parser = NLPParserAgent()
    agent = winAutoAgent()
    
    for command in test_commands:
        print(f"\n执行命令: {command}")
        task = checkMode(command)
        print(f"任务模式: {task}")
        
        str_result = nlp_parser.parse_instruction(command)
        print(f"解析结果: {str_result}")
        
        if str_result:
            agent.execute(str_result)
