"""游客感受度分析引擎"""
import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import Counter


class AnalyticsEngine:
    """分析游客交互数据，生成感受度报告"""

    # 情感关键词词典
    POSITIVE_WORDS = [
        "好", "棒", "赞", "喜欢", "满意", "开心", "惊喜", "推荐", "值得", "不错",
        "漂亮", "壮观", "震撼", "感动", "有趣", "方便", "舒适", "贴心", "专业", "热情",
        "感谢", "谢谢", "很好", "太好了", "厉害", "精彩", "美丽", "优美", "神圣", "庄严"
    ]

    NEGATIVE_WORDS = [
        "差", "烂", "失望", "不满", "不好", "太贵", "拥挤", "排队", "脏", "乱",
        "慢", "等", "无聊", "没意思", "不方便", "找不到", "迷路", "热", "累", "远",
        "贵", "坑", "骗", "难吃", "难看", "破", "旧", "吵", "臭", "差劲"
    ]

    # 关注点分类关键词
    TOPIC_KEYWORDS = {
        "景点介绍": ["大佛", "梵宫", "坛城", "九龙", "祥符", "景点", "看什么", "有什么", "介绍"],
        "游览路线": ["路线", "怎么走", "游览", "参观", "顺序", "推荐路线", "攻略"],
        "门票价格": ["门票", "票价", "多少钱", "价格", "优惠", "免费", "学生票"],
        "交通出行": ["怎么去", "交通", "公交", "地铁", "停车", "自驾", "路线"],
        "美食餐饮": ["吃", "美食", "餐厅", "素斋", "小吃", "特产", "素饼"],
        "历史文化": ["历史", "文化", "佛教", "典故", "由来", "故事", "传说"],
        "住宿服务": ["住", "酒店", "住宿", "民宿", "精舍", "拈花湾"],
        "时间安排": ["几点", "开放", "时间", "多久", "小时", "半天", "一天"],
    }

    def __init__(self, log_path: str = None):
        if log_path is None:
            from pathlib import Path
            self.log_path = Path(__file__).parent.parent / "logs" / "interactions.json"
        else:
            self.log_path = log_path

    def _load_logs(self) -> List[Dict[str, Any]]:
        """加载交互日志"""
        import json
        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """分析单条文本的情感倾向"""
        pos_count = sum(1 for w in self.POSITIVE_WORDS if w in text)
        neg_count = sum(1 for w in self.NEGATIVE_WORDS if w in text)

        if pos_count > neg_count:
            label = "positive"
            score = min(0.5 + pos_count * 0.1, 1.0)
        elif neg_count > pos_count:
            label = "negative"
            score = max(0.5 - neg_count * 0.1, 0.0)
        else:
            label = "neutral"
            score = 0.5

        return {"label": label, "score": round(score, 2),
                "positive_hits": pos_count, "negative_hits": neg_count}

    def classify_topic(self, text: str) -> str:
        """分类用户关注点"""
        scores = {}
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            scores[topic] = sum(1 for kw in keywords if kw in text)
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "其他"

    def generate_report(self, days: int = 7) -> Dict[str, Any]:
        """生成游客感受度报告"""
        logs = self._load_logs()
        if not logs:
            return {"error": "暂无交互数据", "summary": {}, "trends": [], "topics": [],
                    "suggestions": []}

        # 过滤指定天数
        cutoff = datetime.now() - timedelta(days=days)
        recent = []
        for log in logs:
            try:
                ts = datetime.fromisoformat(log.get("timestamp", ""))
                if ts >= cutoff:
                    recent.append(log)
            except (ValueError, TypeError):
                continue

        if not recent:
            recent = logs  # 如果过滤后为空，用全部数据

        # 1. 情感分析
        sentiments = {"positive": 0, "neutral": 0, "negative": 0}
        for log in recent:
            combined = log.get("user_input", "") + log.get("ai_response", "")
            result = self.analyze_sentiment(combined)
            sentiments[result["label"]] += 1
            log["sentiment"] = result

        total = sum(sentiments.values()) or 1
        satisfaction_rate = round((sentiments["positive"] + sentiments["neutral"] * 0.5) / total * 100, 1)

        # 2. 关注点分析
        topic_counter = Counter()
        for log in recent:
            topic = self.classify_topic(log.get("user_input", ""))
            topic_counter[topic] += 1

        topics = [{"topic": t, "count": c, "percentage": round(c / total * 100, 1)}
                  for t, c in topic_counter.most_common(10)]

        # 3. 情感趋势（按天统计）
        daily_data = {}
        for log in recent:
            try:
                day = datetime.fromisoformat(log.get("timestamp", "")).strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                day = "unknown"
            if day not in daily_data:
                daily_data[day] = {"positive": 0, "neutral": 0, "negative": 0, "total": 0}
            s = log.get("sentiment", {}).get("label", "neutral")
            daily_data[day][s] += 1
            daily_data[day]["total"] += 1

        trends = [{"date": d, **v} for d, v in sorted(daily_data.items())]

        # 4. 反馈统计
        feedback_counts = {"good": 0, "neutral": 0, "bad": 0}
        for log in recent:
            fb = log.get("feedback", "")
            if fb in feedback_counts:
                feedback_counts[fb] += 1

        # 5. 生成服务建议
        suggestions = self._generate_suggestions(sentiments, topic_counter, feedback_counts, total)

        # 6. 热门问题
        hot_questions = Counter(log.get("user_input", "") for log in recent if log.get("user_input"))
        hot_questions_list = [{"question": q, "count": c} for q, c in hot_questions.most_common(10)]

        return {
            "period": f"近{days}天",
            "total_interactions": total,
            "summary": {
                "satisfaction_rate": satisfaction_rate,
                "sentiment_distribution": sentiments,
                "feedback_distribution": feedback_counts,
                "avg_response_time": round(
                    sum(log.get("duration", 0) for log in recent) / total, 2
                ) if total else 0,
            },
            "trends": trends,
            "topics": topics,
            "hot_questions": hot_questions_list,
            "suggestions": suggestions,
        }

    def _generate_suggestions(self, sentiments, topic_counter, feedback_counts, total) -> List[Dict[str, str]]:
        """根据分析结果生成服务建议"""
        suggestions = []

        neg_rate = sentiments.get("negative", 0) / total if total else 0
        if neg_rate > 0.2:
            suggestions.append({
                "type": "情感预警",
                "suggestion": f"负面情感占比{round(neg_rate*100,1)}%，建议排查游客不满原因，优化服务质量",
                "priority": "高"
            })

        bad_rate = feedback_counts.get("bad", 0) / sum(feedback_counts.values()) if sum(feedback_counts.values()) else 0
        if bad_rate > 0.15:
            suggestions.append({
                "type": "差评预警",
                "suggestion": f"差评率{round(bad_rate*100,1)}%，建议关注游客反馈中提到的问题并改进",
                "priority": "高"
            })

        for topic, count in topic_counter.most_common(3):
            suggestions.append({
                "type": "热门关注",
                "suggestion": f"「{topic}」是游客最关注的话题（{count}次提问），建议丰富该方面的讲解内容",
                "priority": "中"
            })

        if sentiments.get("positive", 0) / total > 0.6 if total else False:
            suggestions.append({
                "type": "正面反馈",
                "suggestion": "游客整体满意度较高，建议保持当前服务水平，可考虑增加互动形式",
                "priority": "低"
            })

        suggestions.append({
            "type": "数据建议",
            "suggestion": "建议定期更新知识库内容，确保景区信息时效性",
            "priority": "低"
        })

        return suggestions
