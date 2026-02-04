import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import WinAutoAgent, NLPParserAgent
import importlib
from pathlib import Path
import os


def get_agent_instance(agent_type: str, default_agent: WinAutoAgent):
    """根据 agent_type 动态加载并返回对应的 agent 实例。

    改进规则：
    - 扫描 `agent/` 目录中所有以 `_agent.py` 结尾的文件，生成候选模块列表。
    - 首先尝试精确匹配（agent_type -> 文件名前缀），然后尝试别名映射，最后尝试包含/前缀匹配。
    - 类名通过将文件名前缀从 snake_case 转为 PascalCase 并添加 `Agent`（例如 `calendar` -> `CalendarAgent`）来推断。
    - 找不到匹配时，返回 default_agent（通常为 WinAutoAgent）并打印提示。
    """
    if not agent_type:
        return default_agent

    normalized = agent_type.lower().strip()
    agent_dir = Path(__file__).parent / "agent"

    # 列出 agent 目录下所有 *_agent.py 文件并提取候选前缀
    files = [p for p in agent_dir.glob("*_agent.py") if p.is_file()]
    candidates = [f.name[:-len("_agent.py")] for f in files]

    # 1) 精确匹配
    mod_key = None
    if normalized in candidates:
        mod_key = normalized

    # 2) 常见别名映射
    if mod_key is None:
        alias_map = {
            "notebook": "notebook",
            "calendar": "calendar",
            "winauto": "winauto",
            "win_auto": "winauto",
            "default": "winauto",
        }
        mapped = alias_map.get(normalized)
        if mapped and mapped in candidates:
            mod_key = mapped

    # 3) 包含/前缀匹配（更宽松的匹配规则）
    if mod_key is None:
        for c in candidates:
            if c.startswith(normalized) or normalized in c or c in normalized:
                mod_key = c
                break

    if mod_key is None:
        print(f"未找到匹配的 agent (type={agent_type})，回退到 WinAutoAgent。候选: {candidates}")
        return default_agent

    module_name = f"agent.{mod_key}_agent"

    try:
        module = importlib.import_module(module_name)
        # 将 snake_case 转为 PascalCase 作为类名
        class_name = "".join(part.capitalize() for part in mod_key.split("_")) + "Agent"
        AgentClass = getattr(module, class_name, None)
        if AgentClass is None:
            print(f"模块 '{module_name}' 中未找到类 '{class_name}'，回退到 WinAutoAgent。")
            return default_agent
        return AgentClass()
    except Exception as e:
        print(f"加载 agent '{module_name}' 失败: {e}. 回退到 WinAutoAgent。")
        return default_agent


import json

if __name__ == "__main__":
    # 测试不同的应用程序
    test_commands = [
        "帮我打开记事本并输入文字123",
        "启动硬盘管理，再打开计算器",
        "创建下周五公司团建活动，下午2点到5点，在市中心公园举行，导出为 meeting.ics并打开",
        # "打开记事本写一段日记"
    ]

    # 初始化静态 agent
    nlp_parser = NLPParserAgent()
    win_agent = WinAutoAgent()

    # 示例命令（可以替换为录音转写结果）
    # command = "帮我添加一个日历事件，下周五下午2点到5点，在市中心公园举行公司团建活动，并且导入"
    for command in test_commands:
        print(f"\n=== 处理指令: {command} ===")

        # 使用 NLP 解析器将自然语言指令解析为结构化步骤
        steps = nlp_parser.parse_instruction(command)
        print(f"解析结果: {json.dumps(steps, ensure_ascii=False, indent=2)}")

        if steps:
            for step in steps:
                agent_type = step.get("agent_type", "default")
                step_str = json.dumps(step, ensure_ascii=False)

                print(f"\n执行步骤 {step.get('step')}: {step.get('action')}")

                # 动态获取对应 agent（若不存在则回退到 win_agent）
                agent_instance = get_agent_instance(agent_type, win_agent)

                if agent_instance is None:
                    print(f">> 未找到可用的 agent，跳过步骤 {step.get('step')}。")
                    continue

                print(f">> 调用 {agent_instance.__class__.__name__} 执行...")
                try:
                    agent_instance.execute(step_str)
                except Exception as e:
                    print(f"{agent_instance.__class__.__name__} 执行出错: {e}")
