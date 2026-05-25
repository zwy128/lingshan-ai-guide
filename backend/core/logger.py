"""交互日志记录"""
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class InteractionLogger:
    """记录用户交互日志"""

    def __init__(self):
        self.log_dir = Path(__file__).parent.parent / "logs"
        self.log_path = self.log_dir / "interactions.json"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists() or self.log_path.stat().st_size == 0:
            with open(self.log_path, 'w') as f:
                json.dump([], f)

    def _read(self) -> List[Dict[str, Any]]:
        """读取日志，带容错"""
        try:
            with open(self.log_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            with open(self.log_path, 'w') as f:
                json.dump([], f)
            return []

    def _write(self, logs: List[Dict[str, Any]]):
        with open(self.log_path, 'w') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

    def log(self, user_input: str, ai_response: str, model: str = "", voice: str = ""):
        logs = self._read()
        logs.append({
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "ai_response": ai_response,
            "model": model,
            "voice": voice
        })
        self._write(logs)

    def get_stats(self) -> Dict[str, Any]:
        logs = self._read()
        if not logs:
            return {"total_interactions": 0, "today_interactions": 0,
                    "average_length": 0, "popular_models": {}, "popular_voices": {}}
        total = len(logs)
        today = datetime.now().date()
        today_count = sum(1 for log in logs
                          if datetime.fromisoformat(log["timestamp"]).date() == today)
        total_length = sum(len(log.get("user_input", "")) + len(log.get("ai_response", ""))
                           for log in logs)
        model_counts, voice_counts = {}, {}
        for log in logs:
            m = log.get("model", "unknown")
            v = log.get("voice", "unknown")
            model_counts[m] = model_counts.get(m, 0) + 1
            voice_counts[v] = voice_counts.get(v, 0) + 1
        return {
            "total_interactions": total,
            "today_interactions": today_count,
            "average_length": round(total_length / total, 2) if total else 0,
            "popular_models": dict(sorted(model_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
            "popular_voices": dict(sorted(voice_counts.items(), key=lambda x: x[1], reverse=True)[:5])
        }

    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        logs = self._read()
        return logs[-limit:] if logs else []
