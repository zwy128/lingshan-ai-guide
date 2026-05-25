import os
from pathlib import Path
from dotenv import load_dotenv

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
