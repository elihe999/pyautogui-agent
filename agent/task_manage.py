from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate


def checkMode(context: str):
    qwen = ChatOllama(base_url="http://localhost:11434", model="qwen3:0.6b")
    # 定义提示模板
    prompt = ChatPromptTemplate.from_template(
        "帮我判断一句话，找出用户是想用浏览器操作还是直接操作他脑软件，如果是只需要输出1，不是输出0，不要输出任何其他内容，接下来是用户说的内容：{content}。/no_think"
    )
    # 创建对话链：模板 -> 模型 -> 输出
    chain = prompt | qwen
    # 调用链并生成回答
    result = chain.invoke({"content": context})
    print(result.content)

if __name__ == "__main__":
    checkMode("打开记事本并输入文字123")