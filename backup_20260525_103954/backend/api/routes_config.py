"""配置接口 - 返回可用模型和音色"""
from fastapi import APIRouter
from backend.core.config import get_model_list, get_voice_list

router = APIRouter(prefix="/api/config", tags=["配置"])

@router.get("/models")
async def list_models():
    """获取可用模型列表"""
    return {"models": get_model_list()}

@router.get("/voices")
async def list_voices():
    """获取可用音色列表"""
    return {"voices": get_voice_list()}
