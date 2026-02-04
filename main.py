import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import winAutoAgent, NLPParserAgent, NotebookAgent
import json

if __name__ == "__main__":
    # 测试不同的应用程序
    # test_commands = [
    #     "帮我打开记事本并输入文字123",
    #     # "启动硬盘管理，再打开计算器",
    #     # "打开记事本写一段日记"
    # ]
    
    nlp_parser = NLPParserAgent()
    win_agent = winAutoAgent()
    notebook_agent = NotebookAgent()
    
    # for command in test_commands:
    from utils import record_until_silence, transcribe_recorded_audio
    record_until_silence('output.wav')
    command = transcribe_recorded_audio('output.wav')
    print(f"\n{'='*50}")
    print(f"执行命令: {command}")
    
    steps = nlp_parser.parse_instruction(command)
    print(f"解析结果: {json.dumps(steps, ensure_ascii=False, indent=2)}")
    
    if steps:
        for step in steps:
            agent_type = step.get("agent_type", "default")
            step_str = json.dumps(step, ensure_ascii=False)
            
            print(f"\n执行步骤 {step.get('step')}: {step.get('action')}")
            
            if agent_type == "notebook":
                print(">> 调用 NotebookAgent...")
                try:
                    notebook_agent.execute(step_str)
                except Exception as e:
                    print(f"NotebookAgent 执行出错: {e}")
            else:
                print(">> 调用 winAutoAgent...")
                try:
                    win_agent.execute(step_str)
                except Exception as e:
                    print(f"winAutoAgent 执行出错: {e}")
