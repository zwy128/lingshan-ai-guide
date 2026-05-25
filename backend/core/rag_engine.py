from typing import List, Generator

class RAGEngine:
    def __init__(self):
        # 初始化你的LLM和Vector Store
        pass

    def chat(self, query: str, history: List = []) -> str:
        """普通对话（非流式）"""
        # TODO: 替换为您实际的LLM调用
        return f"回复：关于{query}的详细解答..."
    
    def chat_stream(self, query: str, history: List = []) -> Generator[str, None, None]:
        """流式对话接口"""
        # TODO: 替换为您实际的LLM流式调用，例如 llm.stream(query)
        response_text = f"回复：关于{query}的详细解答，这里是流式输出的示例..."
        for char in response_text:
            yield char
