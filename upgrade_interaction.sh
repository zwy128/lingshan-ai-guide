#!/bin/bash

# 交互体验升级脚本
# 功能：打字机效果 + 基础表情联动 + 语音唇形同步准备

echo "🔧 开始交互体验升级..."

# 1. 在 head 中添加表情定义
sed -i '/<style>/a \
/* 表情动画定义 */\
@keyframes expression-neutral { from { opacity: 1; } to { opacity: 1; } }\
@keyframes expression-happy { from { transform: scale(1); } to { transform: scale(1.05); } }\
@keyframes expression-thinking { from { transform: rotate(0deg); } to { transform: rotate(2deg); } }\
' backend/static/avatar-manage.html

# 2. 在全局状态中添加表情控制
sed -i '/let live2dInstances = {};/a \
let currentExpression = "neutral"; // neutral, happy, thinking, sorry\
let typewriterQueue = []; // 打字机队列\
let isTypewriterRunning = false;' backend/static/avatar-manage.html

# 3. 替换 loadModels 函数，添加表情联动
sed -i '/async function loadModels() {/,/^}/c \
async function loadModels() {\
    try {\
        const res = await fetch("/static/live2d/models.json");\
        const data = await res.json();\
        modelList = data.models || [];\
        renderModelGrid();\
        // 默认使用第一个模型（shizuku）\
        if (!currentModelId && modelList.length > 0) {\
            currentModelId = modelList[0].id;\
            selectModel(currentModelId, modelList[0].name);\
        }\
    } catch (e) {\
        console.error("加载模型配置失败:", e);\
        showToast("❌ 加载模型列表失败");\
    }\
}' backend/static/avatar-manage.html

# 4. 添加打字机效果函数
sed -i '/function showToast(msg, ms = 3000) {/i \
// ============ 打字机效果 ============\
function typewriterEffect(element, text, speed = 50) {\
    return new Promise((resolve) => {\
        element.textContent = "";\
        let i = 0;\
        const timer = setInterval(() => {\
            if (i < text.length) {\
                element.textContent += text.charAt(i);\
                i++;\
            } else {\
                clearInterval(timer);\
                resolve();\
            }\
        }, speed);\
    });\
}\
\
// ============ 表情联动控制 ============\
function setExpression(expression) {\
    currentExpression = expression;\
    // 通知Live2D模型切换表情（如果有表情文件）\
    if (live2dInstances[currentModelId]) {\
        try {\
            // 这里使用简单的CSS动画模拟表情变化\
            const container = document.getElementById(`preview-${currentModelId}`);\
            if (container) {\
                container.style.animation = `expression-${expression} 0.5s ease-in-out`;\
            }\
        } catch (e) {\
            console.log("表情切换失败:", e);\
        }\
    }\
}\
\
// ============ AI回复处理 ============\
function handleAIResponse(response) {\
    const chatMessages = document.getElementById("chatMessages");\
    if (!chatMessages) return;\
    \
    const messageDiv = document.createElement("div");\
    messageDiv.className = "message ai-message";\
    \
    const contentDiv = document.createElement("div");\
    contentDiv.className = "message-content";\
    messageDiv.appendChild(contentDiv);\
    \
    chatMessages.appendChild(messageDiv);\
    \
    // 打字机效果显示\
    typewriterEffect(contentDiv, response).then(() => {\
        // 根据回复内容切换表情\
        if (response.includes("开心") || response.includes("高兴") || response.includes("太好了")) {\
            setExpression("happy");\
        } else if (response.includes("思考") || response.includes("想想") || response.includes("嗯...")) {\
            setExpression("thinking");\
        } else if (response.includes("抱歉") || response.includes("对不起") || response.includes("不好意思")) {\
            setExpression("sorry");\
        } else {\
            setExpression("neutral");\
        }\
    });\
}' backend/static/avatar-manage.html

# 5. 修改选择模型函数，初始化Live2D实例
sed -i '/function selectModel(modelId, modelName) {/,/^}/c \
function selectModel(modelId, modelName) {\
    currentModelId = modelId;\
    const model = modelList.find(m => m.id === modelId);\
    \
    localStorage.setItem("selectedModelId", modelId);\
    localStorage.setItem("selectedModelUrl", model ? model.modelUrl : "");\
    localStorage.setItem("selectedModelType", "live2d");\
    localStorage.setItem("selectedModelName", modelName || modelId);\
    \
    // 更新UI\
    document.querySelectorAll(".model-card").forEach(c => c.classList.remove("active"));\
    const card = document.querySelector(`.model-card[data-id="${modelId}"]`);\
    if (card) card.classList.add("active");\
    \
    // 初始化Live2D实例（如果尚未初始化）\
    if (!live2dInstances[modelId] && model.modelUrl) {\
        initLive2DInstance(model);\
    }\
    \
    // 应用当前表情\
    setExpression(currentExpression);\
    \
    showToast(`✅ 已选择: ${modelName}，返回主页生效`);\
}' backend/static/avatar-manage.html

# 6. 添加Live2D实例初始化函数
sed -i '/function loadLive2DThumbnail(model) {/i \
// ============ 初始化Live2D实例（用于表情联动） ============\
function initLive2DInstance(model) {\
    if (!model.modelUrl || typeof Live2DCubismFramework === "undefined") return;\
    \
    try {\
        // 创建简单的Live2D渲染器\
        const container = document.getElementById(`preview-${model.id}`);\
        if (!container) return;\
        \
        const canvas = document.createElement("canvas");\
        canvas.width = 200;\
        canvas.height = 240;\
        canvas.id = `live2d-canvas-${model.id}`;\
        canvas.style.cssText = "position: absolute; top: 0; left: 0; opacity: 0.8;";\
        container.appendChild(canvas);\
        \
        // 加载模型配置\
        fetch(model.modelUrl)\
            .then(res => res.json())\
            .then(config => {\
                // 简单的模型加载（仅用于表情联动）\
                const mocUrl = new URL(config.model.moc, window.location.origin + model.modelUrl).pathname;\
                const textureUrl = new URL(config.model.textures[0], window.location.origin + model.modelUrl).pathname;\
                \
                // 创建简单的Live2D实例\
                const app = new PIXI.Application({\
                    width: canvas.width,\
                    height: canvas.height,\
                    view: canvas,\
                    transparent: true,\
                });\
                \
                const model2 = new PIXI.Live2DModel(model.modelUrl);\
                model2.anchor.set(0.5, 0.5);\
                model2.position.set(canvas.width / 2, canvas.height / 2);\
                app.stage.addChild(model2);\
                \
                live2dInstances[model.id] = {\
                    app: app,\
                    model: model2,\
                    canvas: canvas,\
                };\
                \
                console.log(`Live2D实例已初始化: ${model.id}`);\
            })\
            .catch(e => console.log(`Live2D实例初始化失败: ${model.id}`, e));\
    } catch (e) {\
        console.log(`Live2D实例初始化失败: ${model.id}`, e);\
    }\
}' backend/static/avatar-manage.html

# 7. 修改 loadVisibleThumbnails 函数，添加Live2D实例初始化
sed -i '/function loadVisibleThumbnails() {/,/^}/c \
function loadVisibleThumbnails() {\
    // 检查 Live2D SDK 是否可用\
    if (typeof Live2DCubismFramework === "undefined" && typeof LIVE2DCUBISMCORE === "undefined") {\
        console.log("Live2D SDK 未加载，使用 emoji 缩略图");\
        return;\
    }\
    \
    // 只为前3个模型加载缩略图和初始化实例\
    const visibleModels = modelList.slice(0, 3);\
    visibleModels.forEach(model => {\
        loadLive2DThumbnail(model);\
        // 同时初始化Live2D实例用于表情联动\
        if (!live2dInstances[model.id]) {\
            initLive2DInstance(model);\
        }\
    });\
}' backend/static/avatar-manage.html

# 8. 在HTML底部添加聊天界面（用于演示打字机效果）
sed -i '</head>/i \
<!-- 聊天界面（演示用） -->\
<div id="chatInterface" style="position: fixed; bottom: 20px; right: 20px; width: 320px; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); z-index: 1000; display: none;">\
    <div style="padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 12px 12px 0 0;">\
        <h3 style="margin: 0; font-size: 16px;">🤖 AI助手</h3>\
        <button onclick="toggleChat()" style="position: absolute; top: 10px; right: 10px; background: none; border: none; color: white; cursor: pointer; font-size: 18px;">×</button>\
    </div>\
    <div id="chatMessages" style="height: 200px; overflow-y: auto; padding: 10px; border-bottom: 1px solid #eee;">\
        <div class="message ai-message"><div class="message-content">你好！我是你的AI助手，有什么可以帮你的吗？😊</div></div>\
    </div>\
    <div style="padding: 10px; display: flex; gap: 8px;">\
        <input type="text" id="chatInput" placeholder="输入消息..." style="flex: 1; padding: 8px; border: 1px solid #ddd; border-radius: 6px;">\
        <button onclick="sendMessage()" style="padding: 8px 15px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer;">发送</button>\
    </div>\
</div>' backend/static/avatar-manage.html

# 9. 添加聊天界面样式和函数
sed -i '/function handleUpload(files) {/i \
// ============ 聊天界面控制 ============\
function toggleChat() {\
    const chatInterface = document.getElementById("chatInterface");\
    chatInterface.style.display = chatInterface.style.display === "none" ? "block" : "none";\
}\
\
// ============ 发送消息 ============\
function sendMessage() {\
    const input = document.getElementById("chatInput");\
    const message = input.value.trim();\
    if (!message) return;\
    \
    const chatMessages = document.getElementById("chatMessages");\
    const messageDiv = document.createElement("div");\
    messageDiv.className = "message user-message";\
    messageDiv.innerHTML = `<div class="message-content">${message}</div>`;\
    chatMessages.appendChild(messageDiv);\
    \
    input.value = "";\
    \
    // 模拟AI回复（实际项目中替换为真实API调用）\
    setTimeout(() => {\
        const responses = {\
            "你好": "你好！很高兴见到你！😊",\
            "你好吗": "我很好，谢谢！你呢？",\
            "今天天气": "今天天气真不错，适合出游！☀️",\
            "推荐景点": "我推荐你去参观故宫，非常值得一去！🏯",\
            "谢谢": "不客气！有需要随时找我。😊",\
        };\
        \
        const aiResponse = responses[message] || "我理解你的问题，让我想想... 🤔";\
        handleAIResponse(aiResponse);\
    }, 1000);\
}' backend/static/avatar-manage.html

# 10. 添加浮动按钮触发聊天界面
sed -i '/window.onload = () => {/i \
// ============ 添加浮动聊天按钮 ============\
const chatButton = document.createElement("div");\
chatButton.innerHTML = "💬";\
chatButton.style.cssText = "position: fixed; bottom: 30px; right: 30px; width: 50px; height: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; cursor: pointer; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); z-index: 999;";\
chatButton.onclick = toggleChat;\
document.body.appendChild(chatButton);' backend/static/avatar-manage.html

echo "✅ 交互体验升级完成！"
echo ""
echo "📋 升级内容："
echo "1. ⌨️ 打字机效果：AI回复逐字显示"
echo "2. 😊 基础表情联动：根据AI回复内容切换3种预设表情（中性/开心/思考）"
echo "3. 💬 聊天界面：集成浮动聊天窗口，方便测试交互效果"
echo ""
echo "🔄 下一步："
echo "1. 刷新页面查看效果"
echo "2. 点击右下角💬按钮打开聊天窗口"
echo "3. 发送消息测试打字机效果和表情联动"
echo ""
echo "⚙️ 注意事项："
echo "- 表情联动使用CSS动画模拟，真实Live2D表情需要模型支持表情文件"
echo "- 打字机效果速度可调节（默认50ms/字）"
echo "- 聊天界面为演示用，实际项目中需替换为真实AI API"

