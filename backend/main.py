from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.rag_engine import RAGEngine
from api.routes_config import router
from core.config import settings
import uvicorn
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)

# 初始化 FastAPI 应用
app = FastAPI(
    title="灵山AI导游",
    version="1.0",
    description="灵山景区智能导游助手"
)

# 配置 CORS（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化核心组件
rag = RAGEngine()

# 注册路由
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "灵山AI导游服务运行中", "version": "1.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
    )
