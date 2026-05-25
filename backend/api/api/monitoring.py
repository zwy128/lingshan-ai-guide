"""性能监控API"""
from fastapi import APIRouter
from core.cache import cache_manager
import time

router = APIRouter(prefix="/api/monitoring", tags=["监控"])

@router.get("/cache/status")
async def cache_status():
    """缓存状态"""
    return {
        "cache_size": len(cache_manager.cache),
        "cache_keys": list(cache_manager.cache.keys()),
        "timestamps": cache_manager.timestamps,
        "expiry_config": {
            "model_list": cache_manager.CACHE_EXPIRY.get("model_list", 0),
            "voice_list": cache_manager.CACHE_EXPIRY.get("voice_list", 0),
            "current_config": cache_manager.CACHE_EXPIRY.get("current_config", 0)
        }
    }

@router.get("/cache/clear")
async def clear_cache():
    """清空缓存"""
    cache_manager.clear()
    return {"status": "ok", "message": "缓存已清空"}

@router.get("/performance/stats")
async def performance_stats():
    """性能统计"""
    # 这里可以添加更详细的性能统计
    return {
        "uptime": time.time(),
        "cache_hit_rate": 0.0,  # 需要实际实现统计
        "compression_ratio": "60-80%",  # 预估值
        "average_response_time": "50ms"  # 预估值
    }
