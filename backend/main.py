from fastapi import FastAPI
from core.rag_engine import RAGEngine
from api.routes_config import router
from config import settings
import uvicorn

# 初始化 FastAPI 应用
app = FastAPI(title="灵山AI导游", version="1.0")

# 初始化核心组件
rag = RAGEngine()

# 注册路由
app.include_router(router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host=settings.SERVER_HOST, 
        port=settings.SERVER_PORT
    )
