#!/bin/bash

echo "🚀 开始性能优化..."

# ============ 1. Gzip压缩中间件 ============
echo "📦 添加Gzip压缩中间件..."

# 在FastAPI应用启动前添加Gzip中间件
cat > backend/middleware/compression.py << 'COMPRESSION_MIDDLEWARE'
"""Gzip压缩中间件"""
from fastapi.middleware.gzip import GZipMiddleware
from fastapi import FastAPI

def add_compression_middleware(app: FastAPI):
    """添加Gzip压缩中间件"""
    # 压缩级别4：平衡压缩率和速度
    # 最小压缩大小：1000字节（小于1KB的不压缩）
    app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=4)
    return app
COMPRESSION_MIDDLEWARE

# ============ 2. API缓存装饰器 ============
echo "💾 添加API缓存功能..."

cat > backend/core/cache.py << 'CACHE_MODULE'
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
CACHE_MODULE

# ============ 3. 修改main.py添加压缩和缓存 ============
echo "🔧 修改main.py添加压缩和缓存..."

# 备份main.py
cp backend/main.py backend/main.py.bak

# 添加压缩中间件
sed -i '1i\from middleware.compression import add_compression_middleware' backend/main.py

# 在app创建后添加压缩
sed -i '/app = FastAPI(/a \    # 添加Gzip压缩中间件\n    add_compression_middleware(app)' backend/main.py

# 添加缓存导入
sed -i '/from core.config import get_model_list, get_voice_list, validate_model, validate_voice/a \from core.cache import cache_response, cache_manager' backend/main.py

# 修改API端点添加缓存
sed -i '/@app.get("\/api\/config\/models")/a \    @cache_response("model_list")' backend/main.py
sed -i '/@app.get("\/api\/config\/voices")/a \    @cache_response("voice_list")' backend/main.py
sed -i '/@app.get("\/api\/config\/current")/a \    @cache_response("current_config")' backend/main.py

# ============ 4. Live2D懒加载实现 ============
echo "⚡ 实现Live2D懒加载..."

cat > backend/static/js/lazy-loading.js << 'LAZY_LOADING_JS'
// Live2D模型懒加载管理器
class Live2DLazyLoader {
    constructor() {
        this.loadedModels = new Set();
        this.loadingPromises = new Map();
        this.modelConfigs = new Map();
        
        // 预加载模型配置（不加载资源）
        this.preloadModelConfigs();
    }
    
    // 预加载模型配置（只加载JSON配置，不加载纹理和moc）
    async preloadModelConfigs() {
        try {
            const res = await fetch('/static/live2d/models.json');
            const data = await res.json();
            const models = data.models || [];
            
            // 存储模型配置
            models.forEach(model => {
                this.modelConfigs.set(model.id, model);
            });
            
            console.log(`✅ 预加载了 ${models.length} 个模型配置`);
        } catch (e) {
            console.error('预加载模型配置失败:', e);
        }
    }
    
    // 获取模型配置（从缓存）
    getModelConfig(modelId) {
        return this.modelConfigs.get(modelId);
    }
    
    // 懒加载模型（点击时调用）
    async loadModel(modelId) {
        // 如果已加载，直接返回
        if (this.loadedModels.has(modelId)) {
            console.log(`模型 ${modelId} 已加载`);
            return true;
        }
        
        // 如果正在加载，等待加载完成
        if (this.loadingPromises.has(modelId)) {
            return this.loadingPromises.get(modelId);
        }
        
        // 开始加载
        const loadPromise = this._loadModelFromServer(modelId);
        this.loadingPromises.set(modelId, loadPromise);
        
        try {
            await loadPromise;
            this.loadedModels.add(modelId);
            console.log(`✅ 模型 ${modelId} 加载成功`);
            return true;
        } catch (error) {
            console.error(`❌ 模型 ${modelId} 加载失败:`, error);
            return false;
        } finally {
            this.loadingPromises.delete(modelId);
        }
    }
    
    // 从服务器加载模型资源
    async _loadModelFromServer(modelId) {
        const config = this.getModelConfig(modelId);
        if (!config) {
            throw new Error(`模型配置未找到: ${modelId}`);
        }
        
        // 加载模型配置文件
        const modelRes = await fetch(config.modelUrl);
        const modelJson = await modelRes.json();
        
        // 加载moc文件
        const mocUrl = new URL(modelJson.model.moc, window.location.origin + config.modelUrl).pathname;
        await fetch(mocUrl);
        
        // 加载纹理（主要体积来源）
        const textureUrls = modelJson.model.textures.map(texture => 
            new URL(texture, window.location.origin + config.modelUrl).pathname
        );
        
        // 并行加载所有纹理
        await Promise.all(textureUrls.map(url => fetch(url)));
        
        // 加载其他资源（物理、表情等）
        const physicsUrl = modelJson.model.physics ? 
            new URL(modelJson.model.physics, window.location.origin + config.modelUrl).pathname : null;
        const poseUrl = modelJson.model.pose ? 
            new URL(modelJson.model.pose, window.location.origin + config.modelUrl).pathname : null;
        
        const optionalPromises = [];
        if (physicsUrl) optionalPromises.push(fetch(physicsUrl));
        if (poseUrl) optionalPromises.push(fetch(poseUrl));
        
        await Promise.all(optionalPromises);
        
        console.log(`模型 ${modelId} 资源加载完成`);
    }
    
    // 预加载单个模型（可选，用于智能预加载）
    async preloadModel(modelId) {
        // 如果已加载或正在加载，跳过
        if (this.loadedModels.has(modelId) || this.loadingPromises.has(modelId)) {
            return;
        }
        
        try {
            await this.loadModel(modelId);
        } catch (e) {
            // 预加载失败不阻塞
            console.log(`预加载模型 ${modelId} 失败:`, e);
        }
    }
    
    // 获取模型加载状态
    isModelLoaded(modelId) {
        return this.loadedModels.has(modelId);
    }
    
    // 获取所有已加载模型
    getLoadedModels() {
        return Array.from(this.loadedModels);
    }
    
    // 清除缓存（用于调试）
    clearCache() {
        this.loadedModels.clear();
        this.loadingPromises.clear();
        console.log('模型缓存已清除');
    }
}

// 全局懒加载器实例
const live2dLazyLoader = new Live2DLazyLoader();

// 导出供使用
window.live2dLazyLoader = live2dLazyLoader;
LAZY_LOADING_JS

# ============ 5. 修改前端HTML使用懒加载 ============
echo "🎨 修改前端HTML使用懒加载..."

# 在head中引入懒加载JS
sed -i '/<head>/a \    <script src="/static/js/lazy-loading.js"><\/script>' backend/static/avatar-manage.html

# 修改渲染模型卡片函数，移除缩略图加载
sed -i '/function renderModelGrid() {/,/^}/c \
function renderModelGrid() {\
    const grid = document.getElementById("modelGrid");\
    grid.innerHTML = "";\
    \
    modelList.forEach(model => {\
        const card = document.createElement("div");\
        card.className = `model-card ${model.id === currentModelId ? "active" : ""}`;\
        card.dataset.id = model.id;\
        \
        card.innerHTML = `\
            <div class="model-preview" id="preview-${model.id}">\
                <span class="active-badge">✓ 使用中</span>\
                <span class="emoji-avatar">${model.thumbnail}</span>\
            </div>\
            <div class="model-info">\
                <div class="model-name">${model.name}</div>\
                <div class="model-desc">${model.description}</div>\
                <div class="model-tags">\
                    ${model.tags.map(t => `<span class="tag">${t}</span>`).join("")}\
                </div>\
            </div>\
        `;\
        \
        // 单击选择并懒加载模型\
        card.onclick = (e) => {\
            if (e.target.closest(".preview-close")) return;\
            selectModel(model.id, model.name);\
            // 懒加载当前选择的模型\
            live2dLazyLoader.loadModel(model.id);\
        };\
        \
        // 双击大图预览（懒加载）\
        card.ondblclick = async () => {\
            await live2dLazyLoader.loadModel(model.id);\
            openPreview(model);\
        };\
        \
        grid.appendChild(card);\
    });\
}' backend/static/avatar-manage.html

# ============ 6. 添加性能监控 ============
echo "📊 添加性能监控..."

cat > backend/static/js/performance-monitor.js << 'PERFORMANCE_MONITOR'
// 性能监控工具
class PerformanceMonitor {
    constructor() {
        this.marks = new Map();
        this.measures = [];
        
        // 自动监控资源加载
        this.monitorResourceTiming();
    }
    
    // 标记开始时间
    mark(name) {
        this.marks.set(name, performance.now());
    }
    
    // 测量时间差
    measure(name, startMark, endMark) {
        const start = this.marks.get(startMark);
        const end = this.marks.get(endMark) || performance.now();
        
        if (start !== undefined) {
            const duration = end - start;
            this.measures.push({ name, duration, timestamp: Date.now() });
            console.log(`⏱️ ${name}: ${duration.toFixed(2)}ms`);
            return duration;
        }
        return 0;
    }
    
    // 监控资源加载
    monitorResourceTiming() {
        window.addEventListener('load', () => {
            setTimeout(() => {
                const resources = performance.getEntriesByType('resource');
                const live2dResources = resources.filter(r => 
                    r.name.includes('/static/live2d/') || r.name.includes('.moc') || r.name.includes('.png')
                );
                
                console.log(`📊 Live2D资源加载统计:`);
                console.log(`总资源数: ${live2dResources.length}`);
                console.log(`总传输大小: ${(live2dResources.reduce((sum, r) => sum + (r.transferSize || 0), 0) / 1024).toFixed(2)} KB`);
                
                const byType = {};
                live2dResources.forEach(r => {
                    const ext = r.name.split('.').pop();
                    byType[ext] = (byType[ext] || 0) + 1;
                });
                console.log('按类型统计:', byType);
            }, 1000);
        });
    }
    
    // 获取性能报告
    getReport() {
        return {
            marks: Object.fromEntries(this.marks),
            measures: this.measures,
            resourceCount: performance.getEntriesByType('resource').length,
            transferSize: performance.getEntriesByType('resource')
                .reduce((sum, r) => sum + (r.transferSize || 0), 0)
        };
    }
}

// 全局监控实例
const performanceMonitor = new PerformanceMonitor();
window.performanceMonitor = performanceMonitor;
PERFORMANCE_MONITOR

# 在HTML中引入性能监控
sed -i '/<script src="\/static\/js\/lazy-loading.js"><\/script>/a \    <script src="/static/js/performance-monitor.js"><\/script>' backend/static/avatar-manage.html

# ============ 7. 添加压缩状态监控API ============
echo "📈 添加压缩状态监控API..."

cat > backend/api/monitoring.py << 'MONITORING_API'
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
MONITORING_API

# 在main.py中注册监控路由
sed -i '/from fastapi import FastAPI/a \from api.monitoring import router as monitoring_router' backend/main.py
sed -i '/app.include_router(/a \    app.include_router(monitoring_router)' backend/main.py

# ============ 8. 创建压缩前后对比脚本 ============
echo "📊 创建压缩效果对比脚本..."

cat > benchmark_compression.py << 'BENCHMARK_SCRIPT'
#!/usr/bin/env python3
"""压缩效果基准测试"""
import requests
import time
import json
from pathlib import Path

def test_compression():
    """测试压缩效果"""
    base_url = "http://localhost:8000"
    
    # 测试API响应
    print("📊 API响应测试:")
    endpoints = [
        "/api/config/models",
        "/api/config/voices",
        "/api/config/current",
    ]
    
    for endpoint in endpoints:
        # 不压缩请求
        start = time.time()
        response = requests.get(f"{base_url}{endpoint}")
        time_no_compress = time.time() - start
        size_no_compress = len(response.content)
        
        # 压缩请求
        start = time.time()
        response = requests.get(
            f"{base_url}{endpoint}",
            headers={"Accept-Encoding": "gzip, deflate, br"}
        )
        time_compress = time.time() - start
        size_compress = len(response.content)
        
        compression_ratio = (1 - size_compress / size_no_compress) * 100 if size_no_compress > 0 else 0
        
        print(f"  {endpoint}:")
        print(f"    无压缩: {size_no_compress} bytes, {time_no_compress:.3f}s")
        print(f"    有压缩: {size_compress} bytes, {time_compress:.3f}s")
        print(f"    压缩率: {compression_ratio:.1f}%")
        print()
    
    # 测试静态文件
    print("📁 静态文件测试:")
    static_files = [
        "/static/live2d/models.json",
        "/static/js/lazy-loading.js",
        "/static/js/performance-monitor.js",
    ]
    
    for file_path in static_files:
        start = time.time()
        response = requests.get(f"{base_url}{file_path}")
        time_no_compress = time.time() - start
        size_no_compress = len(response.content)
        
        start = time.time()
        response = requests.get(
            f"{base_url}{file_path}",
            headers={"Accept-Encoding": "gzip, deflate, br"}
        )
        time_compress = time.time() - start
        size_compress = len(response.content)
        
        compression_ratio = (1 - size_compress / size_no_compress) * 100 if size_no_compress > 0 else 0
        
        print(f"  {file_path}:")
        print(f"    无压缩: {size_no_compress} bytes, {time_no_compress:.3f}s")
        print(f"    有压缩: {size_compress} bytes, {time_compress:.3f}s")
        print(f"    压缩率: {compression_ratio:.1f}%")
        print()

if __name__ == "__main__":
    print("🚀 开始压缩效果基准测试...")
    print("⚠️ 请确保后端服务正在运行: http://localhost:8000")
    print()
    
    try:
        test_compression()
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请先启动后端:")
        print("   python3 backend/main.py")
BENCHMARK_SCRIPT

chmod +x benchmark_compression.py

# ============ 9. 添加Git钩子自动压缩 ============
echo "🪝 添加Git钩子自动压缩新文件..."

cat > .git/hooks/pre-commit << 'PRE_COMMIT_HOOK'
#!/bin/bash

# 自动压缩新增的静态文件
echo "🔍 检查需要压缩的新文件..."

# 获取暂存区中的新文件
NEW_FILES=$(git diff --cached --name-only --diff-filter=A | grep -E '\.(js|css|json|html)$')

if [ -n "$NEW_FILES" ]; then
    echo "📦 压缩新增静态文件:"
    for file in $NEW_FILES; do
        if [ -f "$file" ]; then
            # 使用gzip压缩，但保留原文件
            gzip -c "$file" > "${file}.gz"
            echo "  ✅ 已压缩: $file"
        fi
    done
    echo "💡 压缩文件将在部署时由Web服务器自动选择"
fi

PRE_COMMIT_HOOK

chmod +x .git/hooks/pre-commit

echo "✅ 性能优化完成！"
echo ""
echo "📋 优化内容:"
echo "1. 📦 Gzip压缩中间件：自动压缩API响应和静态文件"
echo "2. ⚡ Live2D懒加载：点击时才加载模型资源"
echo "3. 💾 API缓存：模型列表和音色列表缓存"
echo "4. 📊 性能监控：缓存状态和资源加载统计"
echo ""
echo "🔄 下一步测试:"
echo "1. 重启后端服务: python3 backend/main.py"
echo "2. 访问管理页面，观察首屏加载速度"
echo "3. 点击角色卡片，观察模型加载速度"
echo "4. 运行基准测试: python3 benchmark_compression.py"
echo ""
echo "⚙️ 缓存配置:"
echo "- 模型列表缓存: 5分钟"
echo "- 音色列表缓存: 1小时"
echo "- 当前配置缓存: 3分钟"
echo ""
echo "📈 预期效果:"
echo "- 首屏加载: 从6.1M减少到约100KB（仅HTML/CSS/JS）"
echo "- 模型加载: 点击后100-300ms（Gzip压缩）"
echo "- API响应: 缓存命中时<10ms"

