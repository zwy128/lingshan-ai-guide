/**
 * Live2D 管理器 - 支持多形象切换、口型同步、表情同步
 * 兼容 Cubism 2 和 Cubism 4 模型
 */
class Live2DManager {
    constructor() {
        this.app = null;
        this.model = null;
        this.currentModelId = null;
        this.currentModelConfig = null;
        this.isLoaded = false;
        this.container = null;

        // 口型同步参数
        this.mouthOpenValue = 0;
        this.targetMouthOpen = 0;
        this.smoothFactor = 0.3;

        // 表情参数
        this.currentExpression = null;
        this.expressionTimer = null;
        this.expressionQueue = [];

        // 动作参数
        this.currentMotion = null;

        // 音频分析
        this.audioContext = null;
        this.analyser = null;
        this.audioSource = null;
        this.currentVolume = 0;
        this.smoothedVolume = 0;
        this.isSpeaking = false;

        // 模型参数名映射 (Cubism 2 vs Cubism 4)
        this.PARAM_MOUTH_OPEN_Y = 'PARAM_MOUTH_OPEN_Y';
        this.PARAM_EYE_L_OPEN = 'PARAM_EYE_L_OPEN';
        this.PARAM_EYE_R_OPEN = 'PARAM_EYE_R_OPEN';
        this.PARAM_BODY_ANGLE_X = 'PARAM_BODY_ANGLE_X';
        this.PARAM_BODY_ANGLE_Y = 'PARAM_BODY_ANGLE_Y';
        this.PARAM_ANGLE_X = 'PARAM_ANGLE_X';
        this.PARAM_ANGLE_Y = 'PARAM_ANGLE_Y';
        this.PARAM_ANGLE_Z = 'PARAM_ANGLE_Z';
        this.PARAM_EYE_BALL_X = 'PARAM_EYE_BALL_X';
        this.PARAM_EYE_BALL_Y = 'PARAM_EYE_BALL_Y';
        this.PARAM_BROW_L_Y = 'PARAM_BROW_L_Y';
        this.PARAM_BROW_R_Y = 'PARAM_BROW_R_Y';
        this.PARAM_BROW_L_ANGLE = 'PARAM_BROW_L_ANGLE';
        this.PARAM_BROW_R_ANGLE = 'PARAM_BROW_R_ANGLE';

        // 表情预设参数组合
        this.EXPRESSION_PRESETS = {
            neutral: {
                mouthOpen: 0,
                eyeLOpen: 1,
                eyeROpen: 1,
                browLY: 0,
                browRY: 0,
                browLAngle: 0,
                browRAngle: 0,
                bodyAngleX: 0,
                headAngleX: 0,
                headAngleY: 0,
                duration: 0
            },
            happy: {
                mouthOpen: 0.15,
                eyeLOpen: 0.8,
                eyeROpen: 0.8,
                browLY: 0.3,
                browRY: 0.3,
                browLAngle: 0.1,
                browRAngle: 0.1,
                bodyAngleX: 3,
                headAngleX: 3,
                headAngleY: 5,
                duration: 2500
            },
            surprised: {
                mouthOpen: 0.5,
                eyeLOpen: 1.3,
                eyeROpen: 1.3,
                browLY: 0.6,
                browRY: 0.6,
                browLAngle: 0.3,
                browRAngle: 0.3,
                bodyAngleX: -2,
                headAngleX: -2,
                headAngleY: 0,
                duration: 1500
            },
            thinking: {
                mouthOpen: 0,
                eyeLOpen: 0.6,
                eyeROpen: 0.9,
                browLY: -0.2,
                browRY: 0.2,
                browLAngle: -0.1,
                browRAngle: 0.15,
                bodyAngleX: -5,
                headAngleX: -8,
                headAngleY: -5,
                duration: 3000
            },
            sad: {
                mouthOpen: 0,
                eyeLOpen: 0.7,
                eyeROpen: 0.7,
                browLY: -0.4,
                browRY: -0.4,
                browLAngle: -0.3,
                browRAngle: -0.3,
                bodyAngleX: -2,
                headAngleX: -3,
                headAngleY: -8,
                duration: 2500
            },
            angry: {
                mouthOpen: 0.1,
                eyeLOpen: 0.9,
                eyeROpen: 0.9,
                browLY: -0.5,
                browRY: -0.5,
                browLAngle: -0.4,
                browRAngle: -0.4,
                bodyAngleX: 0,
                headAngleX: 0,
                headAngleY: 3,
                duration: 2000
            },
            greeting: {
                mouthOpen: 0.2,
                eyeLOpen: 1,
                eyeROpen: 1,
                browLY: 0.4,
                browRY: 0.4,
                browLAngle: 0.15,
                browRAngle: 0.15,
                bodyAngleX: 5,
                headAngleX: 5,
                headAngleY: 8,
                duration: 2000
            },
            explaining: {
                mouthOpen: 0.1,
                eyeLOpen: 1,
                eyeROpen: 1,
                browLY: 0.15,
                browRY: 0.15,
                browLAngle: 0.05,
                browRAngle: 0.05,
                bodyAngleX: 2,
                headAngleX: 2,
                headAngleY: 3,
                duration: 0  // 持续直到说话结束
            }
        };

        // 动画帧循环
        this._animationFrame = null;
        this._startAnimationLoop();
    }

    /**
     * 初始化 PIXI 应用并加载模型
     */
    async init(container, modelConfig) {
        this.container = container;
        this.currentModelConfig = modelConfig;

        // 清理旧实例
        await this.destroy();

        // 显示加载状态
        container.innerHTML = `
            <div style="color:white;text-align:center;padding-top:120px">
                <div style="width:30px;height:30px;border:3px solid rgba(255,255,255,.3);border-top-color:white;border-radius:50%;animation:spin .8s linear infinite;margin:0 auto 10px"></div>
                加载模型中...
            </div>`;

        try {
            // 检查 PIXI 和 Live2D 库
            if (typeof PIXI === 'undefined') {
                throw new Error('PIXI.js 未加载');
            }
            if (!PIXI.live2d || !PIXI.live2d.Live2DModel) {
                throw new Error('pixi-live2d-display 库未加载，请检查 CDN 引用');
            }

            // 创建 PIXI 应用
            const width = container.clientWidth || 380;
            const height = 450;
            this.app = new PIXI.Application({
                width,
                height,
                transparent: true,
                autoDensity: true,
                resolution: window.devicePixelRatio || 2,
                antialias: true
            });

            container.innerHTML = '';
            container.appendChild(this.app.view);

            // 加载模型
            const model = await PIXI.live2d.Live2DModel.from(modelConfig.modelUrl);
            this.model = model;
            this.app.stage.addChild(model);

            // 设置模型位置和缩放
            model.anchor.set(0.5, 0.5);
            model.x = this.app.screen.width / 2;
            model.y = this.app.screen.height / 2;
            const scale = Math.min(
                this.app.screen.width / model.width,
                this.app.screen.height / model.height
            );
            model.scale.set(scale * 0.85);

            // 注入口型同步到模型更新循环
            this._injectMouthSync();

            // 添加名称显示
            this._addNameDisplay(modelConfig.name || '数字人');

            this.currentModelId = modelConfig.id;
            this.isLoaded = true;

            // 尝试加载模型自带表情
            await this._loadModelExpressions(modelConfig);

            // 播放待机动作
            this.playExpression('greeting');

            console.log(`[Live2DManager] 模型加载成功: ${modelConfig.name} (${modelConfig.id})`);
            return true;
        } catch (e) {
            console.error('[Live2DManager] 模型加载失败:', e);
            container.innerHTML = `
                <div style="color:white;padding:40px;text-align:center">
                    模型加载失败<br>
                    <small>${e.message}</small><br><br>
                    <button onclick="window.live2dManager.destroy();window.restoreSVG?.()"
                        style="background:#667eea;color:white;border:none;padding:8px 20px;border-radius:15px;cursor:pointer">
                        恢复默认
                    </button>
                </div>`;
            this.isLoaded = false;
            return false;
        }
    }

    /**
     * 注入口型同步到模型核心更新循环
     */
    _injectMouthSync() {
        if (!this.model || !this.model.internalModel) return;

        try {
            const coreModel = this.model.internalModel.coreModel;
            const origUpdate = coreModel.update.bind(coreModel);

            // 检测可用的参数名（不同模型可能使用不同的参数名）
            this._detectMouthParamName(coreModel);

            coreModel.update = (...args) => {
                // 口型同步 - 平滑插值
                if (this.isSpeaking) {
                    const rawVolume = this.currentVolume < 0.02 ? 0 : this.currentVolume;
                    const amplified = Math.min(1, Math.pow(rawVolume * 12, 1.2));

                    if (amplified > this.smoothedVolume) {
                        this.smoothedVolume += (amplified - this.smoothedVolume) * 0.5;
                    } else {
                        this.smoothedVolume = Math.max(amplified, this.smoothedVolume - 0.08);
                    }
                } else {
                    this.smoothedVolume *= 0.85; // 平滑关闭
                }

                // 设置嘴巴张开参数（尝试多种可能的参数名）
                try {
                    const mouthValue = Math.max(0, Math.min(1, this.smoothedVolume));
                    const paramNames = ['PARAM_MOUTH_OPEN_Y', 'MouthOpenY', 'MOUTH_OPEN', 'mouthOpen', 'ParamMouthOpenY'];
                    for (const name of paramNames) {
                        try {
                            coreModel.setParamFloat(name, mouthValue);
                            break;
                        } catch (e) { /* 尝试下一个参数名 */ }
                    }
                } catch (e) { /* 参数不存在则跳过 */ }

                origUpdate(...args);
            };
        } catch (e) {
            console.warn('[Live2DManager] 口型同步注入失败:', e);
        }
    }

    /**
     * 检测模型支持的口型参数名
     */
    _detectMouthParamName(coreModel) {
        try {
            const paramNames = ['PARAM_MOUTH_OPEN_Y', 'MouthOpenY', 'MOUTH_OPEN', 'mouthOpen', 'ParamMouthOpenY'];
            for (const name of paramNames) {
                try {
                    coreModel.getParamFloat(name);
                    this.PARAM_MOUTH_OPEN_Y = name;
                    return;
                } catch (e) { /* 尝试下一个 */ }
            }
        } catch (e) { /* 忽略 */ }
    }

    /**
     * 加载模型自带的表情文件
     */
    async _loadModelExpressions(modelConfig) {
        if (!this.model || !this.model.internalModel) return;

        try {
            // 尝试通过 settings 获取表情列表
            const settings = this.model.internalModel.settings;
            if (settings && settings.expressions) {
                console.log(`[Live2DManager] 发现 ${settings.expressions.length} 个内置表情`);
            }
        } catch (e) {
            console.log('[Live2DManager] 无内置表情，使用参数驱动');
        }
    }

    /**
     * 添加名称显示
     */
    _addNameDisplay(name) {
        const existing = this.container.querySelector('.name-display');
        if (existing) existing.remove();

        const nameDiv = document.createElement('div');
        nameDiv.className = 'name-display';
        nameDiv.innerHTML = `<span style="color:#00ff88">●</span> <span id="guideNameText">${name}</span><div class="role">AI 智慧导游</div>`;
        this.container.appendChild(nameDiv);
    }

    /**
     * 播放表情
     * @param {string} expressionName - 表情名称 (neutral/happy/surprised/thinking/sad/angry/greeting/explaining)
     * @param {number} duration - 持续时间(ms)，0表示持续到下次切换
     */
    playExpression(expressionName, duration) {
        if (!this.model || !this.model.internalModel) return;

        const preset = this.EXPRESSION_PRESETS[expressionName];
        if (!preset) {
            console.warn(`[Live2DManager] 未知表情: ${expressionName}`);
            return;
        }

        // 清除之前的表情定时器
        if (this.expressionTimer) {
            clearTimeout(this.expressionTimer);
            this.expressionTimer = null;
        }

        this.currentExpression = expressionName;

        // 尝试使用模型内置表情
        if (this._tryPlayBuiltinExpression(expressionName)) {
            const dur = duration || preset.duration;
            if (dur > 0) {
                this.expressionTimer = setTimeout(() => {
                    this.playExpression('neutral');
                }, dur);
            }
            return;
        }

        // 降级：使用参数驱动表情
        this._applyExpressionParams(preset);

        const dur = duration || preset.duration;
        if (dur > 0) {
            this.expressionTimer = setTimeout(() => {
                this.playExpression('neutral');
            }, dur);
        }
    }

    /**
     * 尝试播放模型内置表情
     */
    _tryPlayBuiltinExpression(expressionName) {
        try {
            // 映射表情名到模型表情索引
            const expressionMap = {
                happy: [0, 1],      // 尝试索引 0 或 1
                surprised: [2, 3],
                sad: [3, 4],
                angry: [4, 5],
                neutral: []
            };

            const indices = expressionMap[expressionName];
            if (!indices || indices.length === 0) return false;

            const settings = this.model.internalModel.settings;
            if (!settings || !settings.expressions || settings.expressions.length === 0) return false;

            // 找到可用的表情索引
            for (const idx of indices) {
                if (idx < settings.expressions.length) {
                    this.model.expression(idx);
                    console.log(`[Live2DManager] 播放内置表情 #${idx}`);
                    return true;
                }
            }
            return false;
        } catch (e) {
            return false;
        }
    }

    /**
     * 使用参数驱动表情（降级方案）
     */
    _applyExpressionParams(preset) {
        if (!this.model || !this.model.internalModel) return;

        try {
            const coreModel = this.model.internalModel.coreModel;
            const setParam = (name, value) => {
                try { coreModel.setParamFloat(name, value); } catch (e) { /* 忽略不存在的参数 */ }
            };

            // 平滑过渡到目标参数
            const animate = () => {
                setParam(this.PARAM_EYE_L_OPEN, preset.eyeLOpen);
                setParam(this.PARAM_EYE_R_OPEN, preset.eyeROpen);
                setParam(this.PARAM_BROW_L_Y, preset.browLY);
                setParam(this.PARAM_BROW_R_Y, preset.browRY);
                setParam(this.PARAM_BROW_L_ANGLE, preset.browLAngle);
                setParam(this.PARAM_BROW_R_ANGLE, preset.browRAngle);
                setParam(this.PARAM_BODY_ANGLE_X, preset.bodyAngleX);
                setParam(this.PARAM_ANGLE_X, preset.headAngleX);
                setParam(this.PARAM_ANGLE_Y, preset.headAngleY);
            };

            animate();
        } catch (e) {
            console.warn('[Live2DManager] 参数驱动表情失败:', e);
        }
    }

    /**
     * 播放动作
     */
    playMotion(group, index) {
        if (!this.model) return;
        try {
            this.model.motion(group || '', index || 0);
        } catch (e) {
            // 某些模型不支持动作
        }
    }

    /**
     * 开始说话 - 启动口型同步
     */
    startSpeaking() {
        this.isSpeaking = true;
        this.smoothedVolume = 0;

        // 说话时播放解释表情
        if (this.currentExpression === 'neutral' || !this.currentExpression) {
            this.playExpression('explaining');
        }
    }

    /**
     * 停止说话 - 停止口型同步
     */
    stopSpeaking() {
        this.isSpeaking = false;
        this.smoothedVolume = 0;
        this.currentVolume = 0;

        // 说话结束后恢复中性表情
        if (this.expressionTimer) {
            clearTimeout(this.expressionTimer);
        }
        this.expressionTimer = setTimeout(() => {
            this.playExpression('neutral');
        }, 500);
    }

    /**
     * 根据文本情感播放表情
     * @param {string} text - AI 回复文本
     */
    playExpressionFromText(text) {
        const sentiment = this._analyzeSentiment(text);
        this.playExpression(sentiment);
    }

    /**
     * 简单的中文情感分析
     */
    _analyzeSentiment(text) {
        // 关键词情感映射
        const emotionKeywords = {
            happy: ['高兴', '开心', '快乐', '欢喜', '幸福', '美好', '精彩', '壮观', '壮丽', '美丽',
                     '欢迎', '恭喜', '祝贺', '太好了', '不错', '很好', '棒', '赞', '喜欢', '爱',
                     '微笑', '笑', '乐', '欢', '喜', '吉祥', '如意', '祝福', '祈福', '许愿',
                     '金碧辉煌', '宏伟', '震撼', '绝美', '灿烂', '辉煌', '瑰丽', '典雅'],
            surprised: ['惊讶', '意外', '没想到', '竟然', '居然', '天哪', '哇', '不可思议',
                        '难以置信', '震惊', '吃惊', '神奇', '奇迹', '罕见', '独特'],
            sad: ['遗憾', '可惜', '难过', '伤心', '悲伤', '不幸', '惋惜', '感叹', '沧桑',
                  '衰落', '消失', '失去', '离别', '思念', '忧愁'],
            angry: ['生气', '愤怒', '不满', '讨厌', '可恶', '岂有此理', '不可接受'],
            thinking: ['思考', '考虑', '想想', '分析', '研究', '探讨', '也许', '可能', '大概',
                       '据说', '传说', '相传', '据说', '据说'],
            greeting: ['你好', '您好', '欢迎', '嗨', '早上好', '下午好', '晚上好', '初次见面']
        };

        let maxScore = 0;
        let dominantEmotion = 'neutral';

        for (const [emotion, keywords] of Object.entries(emotionKeywords)) {
            let score = 0;
            for (const keyword of keywords) {
                if (text.includes(keyword)) {
                    score += keyword.length; // 长关键词权重更高
                }
            }
            if (score > maxScore) {
                maxScore = score;
                dominantEmotion = emotion;
            }
        }

        // 标点符号增强
        if (text.includes('！') || text.includes('!')) {
            if (dominantEmotion === 'neutral') dominantEmotion = 'happy';
        }
        if (text.includes('？') || text.includes('?')) {
            if (dominantEmotion === 'neutral') dominantEmotion = 'thinking';
        }
        if (text.includes('…') || text.includes('......')) {
            if (dominantEmotion === 'neutral') dominantEmotion = 'thinking';
        }

        return dominantEmotion;
    }

    /**
     * 初始化音频分析器
     */
    initAudioAnalyser(audioElement) {
        try {
            if (!this.audioContext) {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            }

            if (this.audioContext.state === 'suspended') {
                this.audioContext.resume();
            }

            // 创建新的 analyser（每次都创建新的，避免缓存问题）
            if (this.analyser) {
                try { this.analyser.disconnect(); } catch (e) {}
            }
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 256;
            this.analyser.smoothingTimeConstant = 0.8;

            // 创建新的 audioSource 并连接到新的 analyser
            if (this.audioSource) {
                try { this.audioSource.disconnect(); } catch (e) {}
            }
            this.audioSource = this.audioContext.createMediaElementSource(audioElement);
            this.audioSource.connect(this.analyser);
            this.analyser.connect(this.audioContext.destination);

            // 开始音量监测
            this._startVolumeMonitoring();
        } catch (e) {
            console.warn('[Live2DManager] 音频分析器初始化失败:', e);
        }
    }

    /**
     * 开始音量监测
     */
    _startVolumeMonitoring() {
        const updateVolume = () => {
            if (!this.analyser) return;

            const dataArray = new Uint8Array(this.analyser.frequencyBinCount);
            this.analyser.getByteTimeDomainData(dataArray);

            let sum = 0;
            for (let i = 0; i < dataArray.length; i++) {
                const val = (dataArray[i] - 128) / 128;
                sum += val * val;
            }
            this.currentVolume = Math.sqrt(sum / dataArray.length);

            // 始终运行音量监测，而不是只在 speaking 时运行
            requestAnimationFrame(updateVolume);
        };

        updateVolume();
    }

    /**
     * 动画循环
     */
    _startAnimationLoop() {
        const loop = () => {
            this._animationFrame = requestAnimationFrame(loop);

            // 空闲时的微动画（呼吸、轻微摆动）
            if (this.isLoaded && this.model && !this.isSpeaking && this.currentExpression === 'neutral') {
                this._idleAnimation();
            }
        };
        loop();
    }

    /**
     * 空闲微动画
     */
    _idleAnimation() {
        if (!this.model || !this.model.internalModel) return;

        try {
            const coreModel = this.model.internalModel.coreModel;
            const time = Date.now() / 1000;

            // 轻微呼吸效果
            const breathValue = Math.sin(time * 1.5) * 0.02;
            try { coreModel.addParamFloat(this.PARAM_BODY_ANGLE_X, breathValue); } catch (e) {}

            // 轻微头部摆动
            const headSway = Math.sin(time * 0.8) * 0.5;
            try { coreModel.addParamFloat(this.PARAM_ANGLE_Z, headSway); } catch (e) {}

        } catch (e) { /* 忽略 */ }
    }

    /**
     * 切换模型
     */
    async switchModel(modelConfig) {
        console.log(`[Live2DManager] 切换模型: ${modelConfig.name}`);
        const result = await this.init(this.container, modelConfig);
        return result;
    }

    /**
     * 销毁当前实例
     */
    async destroy() {
        if (this.expressionTimer) {
            clearTimeout(this.expressionTimer);
            this.expressionTimer = null;
        }

        if (this._animationFrame) {
            cancelAnimationFrame(this._animationFrame);
            this._animationFrame = null;
        }

        if (this.app) {
            try {
                this.app.destroy(true);
            } catch (e) { /* 忽略 */ }
            this.app = null;
        }

        this.model = null;
        this.isLoaded = false;
        this.currentModelId = null;
        this.currentExpression = null;
        this.isSpeaking = false;
        this.smoothedVolume = 0;
        this.currentVolume = 0;

        // 重置音频源（不关闭 AudioContext，因为可能复用）
        this.audioSource = null;
    }

    /**
     * 获取当前状态
     */
    getStatus() {
        return {
            isLoaded: this.isLoaded,
            currentModelId: this.currentModelId,
            currentExpression: this.currentExpression,
            isSpeaking: this.isSpeaking,
            currentVolume: this.currentVolume
        };
    }
}

// 全局单例
window.live2dManager = new Live2DManager();
