import json, os, time
from datetime import date, timedelta
from collections import Counter
from threading import Lock

class InteractionLogger:
    def __init__(self, log_path="../data/interaction_log.json"):
        self.log_path = log_path
        self.feedback_path = "../data/feedback_log.json"
        self.lock = Lock()
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        if not os.path.exists(log_path):
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump([], f)
        if not os.path.exists(self.feedback_path):
            with open(self.feedback_path, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def _read(self, path):
        with self.lock:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)

    def _write(self, path, data):
        with self.lock:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    def add(self, question, answer, duration=0.0, source="text"):
        entry = {
            "timestamp": time.time(),
            "date": str(date.today()),
            "question": question,
            "answer": answer[:200],
            "duration": duration,
            "source": source
        }
        logs = self._read(self.log_path)
        logs.append(entry)
        self._write(self.log_path, logs)

    def add_feedback(self, rating):
        """rating: 'good', 'neutral', 'bad'"""
        entry = {
            "timestamp": time.time(),
            "date": str(date.today()),
            "rating": rating
        }
        feedbacks = self._read(self.feedback_path)
        feedbacks.append(entry)
        self._write(self.feedback_path, feedbacks)

    def get_stats(self):
        logs = self._read(self.log_path)
        today = str(date.today())
        today_logs = [l for l in logs if l["date"] == today]
        today_count = len(today_logs)
        week_logs = [l for l in logs if date.fromisoformat(l["date"]) >= date.today() - timedelta(days=date.today().weekday())]
        week_count = len(week_logs)
        question_counter = Counter(l["question"] for l in week_logs)
        top_questions = [{"q": q, "count": c} for q, c in question_counter.most_common(5)]
        avg_duration = sum(l["duration"] for l in week_logs) / len(week_logs) if week_logs else 0

        # 满意度从反馈日志中计算
        feedbacks = self._read(self.feedback_path)
        if feedbacks:
            good_count = sum(1 for f in feedbacks if f.get("rating") == "good")
            satisfaction = round(good_count / len(feedbacks) * 100, 1)
        else:
            satisfaction = None  # 无数据时前端显示为 "暂无"

        return {
            "today_visitors": today_count,
            "week_visitors": week_count,
            "avg_response_time": round(avg_duration, 2),
            "satisfaction_rate": satisfaction,
            "top_questions": top_questions
        }

    def get_recent(self, limit=20):
        logs = self._read(self.log_path)
        return logs[-limit:]
