from typing import List

class KnowledgeBase:
    def __init__(self):
        # TODO: 初始化 Embedding 模型和 Vector Store
        pass

    def retrieve(self, query: str, top_k: int = 5, score_threshold: float = 0.7) -> List[str]:
        """
        优化检索策略：
        1. 增加 top_k 以获取更多候选集
        2. 加入 score_threshold 过滤低质量相关文档，减少幻觉
        """
        # 模拟检索逻辑
        # docs = vector_store.similarity_search_with_score(query, k=top_k)
        # filtered_docs = [doc for doc, score in docs if score >= score_threshold]
        filtered_docs = [f"与'{query}'高度相关的景区介绍文档..."]
        return filtered_docs
