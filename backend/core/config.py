import os
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List

# 加载 .env 文件
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    """项目配置 - 从 .env 读取，避免密钥硬编码"""

    # LLM 配置
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo")

    # Embedding 配置
    EMBEDDING_API_KEY: str = os.getenv("EMBEDDING_API_KEY", os.getenv("LLM_API_KEY", ""))
    EMBEDDING_BASE_URL: str = os.getenv("EMBEDDING_BASE_URL", os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"))
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "text-embedding-ada-002")

    # ASR 配置
    ASR_API_KEY: str = os.getenv("ASR_API_KEY", os.getenv("LLM_API_KEY", ""))
    ASR_BASE_URL: str = os.getenv("ASR_BASE_URL", os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"))

    # TTS 配置
    TTS_API_KEY: str = os.getenv("TTS_API_KEY", os.getenv("LLM_API_KEY", ""))
    TTS_BASE_URL: str = os.getenv("TTS_BASE_URL", os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"))

    # 服务器配置
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))


settings = Settings()


# ========== 模型与音色配置 ==========

@dataclass
class VoiceOption:
    id: str
    name: str
    gender: str
    style: str


@dataclass
class ModelOption:
    id: str
    name: str
    desc: str
    speed: str
    context_length: str
    input_price: str
    output_price: str


MODELS: List[ModelOption] = [
    ModelOption("qwen-turbo", "通义千问-Turbo", "极速响应，适合简单问答", "快", "1M tokens", "0.3元/百万", "0.6元/百万"),
    ModelOption("qwen-plus", "通义千问-Plus", "均衡之选，推荐使用", "中", "1M tokens", "0.8元/百万", "2元/百万"),
    ModelOption("qwen-max", "通义千问-Max", "最强推理，复杂问题首选", "慢", "32K tokens", "2.4元/百万", "9.6元/百万"),
]

VOICES: List[VoiceOption] = [
    VoiceOption("zh-CN-XiaoxiaoNeural", "晓晓", "female", "温柔亲切"),
    VoiceOption("zh-CN-XiaoyiNeural", "晓伊", "female", "活泼可爱"),
    VoiceOption("zh-CN-YunjianNeural", "云健", "male", "磁性沉稳"),
    VoiceOption("zh-CN-YunxiNeural", "云希", "male", "阳光清新"),
    VoiceOption("zh-CN-YunxiaNeural", "云夏", "male", "少年清朗"),
    VoiceOption("zh-CN-XiaochenNeural", "晓辰", "female", "知性大方"),
    VoiceOption("zh-CN-XiaohanNeural", "晓涵", "female", "温暖治愈"),
    VoiceOption("zh-CN-XiaomengNeural", "晓梦", "female", "甜美灵动"),
    VoiceOption("zh-CN-XiaomoNeural", "晓墨", "female", "优雅文艺"),
    VoiceOption("zh-CN-XiaoruiNeural", "晓瑞", "female", "沉稳干练"),
    VoiceOption("zh-CN-XiaoshuangNeural", "晓双", "female", "童声天真"),
    VoiceOption("zh-CN-XiaoxuanNeural", "晓萱", "female", "柔美细腻"),
    VoiceOption("zh-CN-XiaozhenNeural", "晓甄", "female", "自然舒适"),
]


def get_model_list():
    return [{"id": m.id, "name": m.name, "desc": m.desc, "speed": m.speed,
             "context_length": m.context_length, "input_price": m.input_price,
             "output_price": m.output_price} for m in MODELS]


def get_voice_list():
    return [{"id": v.id, "name": v.name, "gender": v.gender, "style": v.style} for v in VOICES]


def validate_model(model_id: str) -> str:
    """验证模型ID，无效则返回默认"""
    valid_ids = [m.id for m in MODELS]
    return model_id if model_id in valid_ids else "qwen-plus"


def validate_voice(voice_id: str) -> str:
    """验证音色ID，无效则返回默认"""
    valid_ids = [v.id for v in VOICES]
    return voice_id if voice_id in valid_ids else "zh-CN-XiaoxiaoNeural"
