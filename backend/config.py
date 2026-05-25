import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class Settings:
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "default-model")
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "./data/default_db")
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", 8000))

settings = Settings()
