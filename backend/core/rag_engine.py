"""RAG 问答引擎"""
import os
import sys
sys.path.insert(0, '/home/zwy1128/tour-guide-ai/backend')
from core.knowledge_base import KnowledgeBase
from openai import OpenAI

class RAGEngine:
    def __init__(self):
        self.kb = KnowledgeBase()
        self.client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.model = "qwen-plus"
        self.system_prompt = """你是灵山胜境景区的AI数字导游"小灵"。热情亲切。仅根据参考资料回答，不要编造。回答80-150字。"""
    
    def answer(self, user_query: str) -> dict:
        retrieved_docs = self.kb.search(user_query, k=4)
        context = "\n\n".join([f"[来源: {d['source']}]\n{d['content']}" for d in retrieved_docs])
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"【参考资料】\n{context}\n\n【用户问题】\n{user_query}"}
            ],
            temperature=0.7,
            max_tokens=300
        )
        return {
            "question": user_query,
            "answer": response.choices[0].message.content,
            "sources": list(set([d['source'] for d in retrieved_docs])),
        }
