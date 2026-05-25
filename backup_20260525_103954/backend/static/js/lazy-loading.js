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
