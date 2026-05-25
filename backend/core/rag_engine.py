"""RAG 问答引擎"""
import os
import sys
from core.knowledge_base import KnowledgeBase
from openai import OpenAI


def remove_emoji(text):
    import re
    # 匹配常见的表情符号、象形符号、箭头等
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F]"  # 表情符号
        "|[\U0001F300-\U0001F5FF]"  # 符号和象形文字
        "|[\U0001F680-\U0001F6FF]"  # 交通和地图符号
        "|[\U0001F1E0-\U0001F1FF]"  # 旗帜
        "|[\U00002702-\U000027B0]"  # 其他符号
        "|[\U000024C2-\U0001F251]"  # 封闭式字母数字补充
        "|[\U0001F900-\U0001F9FF]"  # 补充符号和象形文字
        "|[\U0001FA00-\U0001FA6F]"  # 扩展-A
        "|[\U0001FA70-\U0001FAFF]"  # 扩展-A 符号
        "|[\U00002600-\U000026FF]"  # 杂项符号
        "|[\U0000FE00-\U0000FE0F]"  # 变体选择符
        "|[\U0000200D]"  # 零宽连接符
        "|[\U000020E3]"  # 组合封闭式按键帽
        "|[\U0000231A-\U0000231B]"  # 手表、沙漏
        "|[\U000023E9-\U000023F3]"  # 双三角等
        "|[\U000023F8-\U000023FA]"  # 控制符号
        "|[\U00002B06]"  # 上箭头等（部分）
        "|[\u2600-\u27BF]"  # 各种符号
        "|[\u2B50]"  # 星星
        "+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

class RAGEngine:
    def set_model(self, model_id: str):
        """动态设置模型"""
        from core.config import validate_model
        self.current_model = validate_model(model_id)
        self.model = self.current_model  # 更新实际使用的模型

    def __init__(self):
        self.kb = KnowledgeBase()
        self.client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.model = "qwen-plus"  # 默认模型
        self.current_model = "qwen-plus"  # 当前使用的模型
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

    def clear_history(self):
        """清除对话历史"""
        self.history = []
        return {"status": "ok"}
    
