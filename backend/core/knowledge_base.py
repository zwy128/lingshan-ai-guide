from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """知识库检索引擎 - 优化检索质量，减少幻觉"""

    def __init__(self):
        # TODO: 初始化 Embedding 模型和 Vector Store
        logger.info("Knowledge Base 初始化中...")

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.6,
    ) -> List[Dict]:
        """
        优化检索策略：
        1. 增加 top_k (默认5) 获取更多候选文档
        2. 设置 score_threshold (默认0.6) 过滤低质量相关文档
        3. 返回包含内容和分数的结构化结果

        Args:
            query: 用户查询
            top_k: 返回的最大文档数
            score_threshold: 相关性分数阈值，低于此值的文档被过滤

        Returns:
            List[Dict]: 包含 content 和 score 的文档列表
        """
        # TODO: 替换为实际的向量检索
        # docs_with_scores = vector_store.similarity_search_with_score(query, k=top_k)
        # filtered = [
        #     {"content": doc.page_content, "score": float(score)}
        #     for doc, score in docs_with_scores
        #     if score >= score_threshold
        # ]

        # 模拟返回
        filtered = [
            {
                "content": f"灵山景区位于江西省上饶市广信区，是国家5A级旅游景区...",
                "score": 0.92,
            }
        ]
        logger.info(f"检索到 {len(filtered)} 条相关文档 (阈值: {score_threshold})")
        return filtered

    def build_prompt(self, query: str, docs: List[Dict]) -> str:
        """基于检索结果构建 prompt，减少幻觉"""
        context = "\n\n".join(
            [f"[文档{i+1}](相关度:{d['score']:.2f}): {d['content']}" for i, d in enumerate(docs)]
        )
        prompt = f"""你是一个专业的灵山景区导游AI助手。请根据以下参考资料回答游客的问题。
如果参考资料中没有相关信息，请诚实地说"我不太确定"，不要编造信息。

参考资料：
{context}

游客问题：{query}

请用友好、专业的语气回答："""
        return prompt
