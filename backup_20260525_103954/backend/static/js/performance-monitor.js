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
