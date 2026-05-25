"""API缓存模块"""
from functools import lru_cache
import time
from typing import Dict, Any, Optional

# 缓存过期时间（秒）
CACHE_EXPIRY = {
    "model_list": 300,  # 模型列表5分钟
    "voice_list": 3600,  # 音色列表1小时
    "config": 180,      # 配置3分钟
}

class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self.timestamps: Dict[str, float] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key not in self.cache:
            return None
        
        # 检查过期时间
        if key in CACHE_EXPIRY:
            if time.time() - self.timestamps[key] > CACHE_EXPIRY[key]:
                # 过期，删除缓存
                del self.cache[key]
                del self.timestamps[key]
                return None
        
        return self.cache[key]
    
    def set(self, key: str, value: Any):
        """设置缓存"""
        self.cache[key] = value
        self.timestamps[key] = time.time()
    
    def clear(self):
        """清空所有缓存"""
        self.cache.clear()
        self.timestamps.clear()
    
    def remove(self, key: str):
        """删除特定缓存"""
        if key in self.cache:
            del self.cache[key]
            del self.timestamps[key]

# 全局缓存实例
cache_manager = CacheManager()

def cache_response(cache_key: str, expiry_key: str = "config"):
    """API响应缓存装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 检查缓存
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 设置缓存
            cache_manager.set(cache_key, result)
            
            return result
        return wrapper
    return decorator
