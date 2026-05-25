// 实际AI API集成
const API_BASE = '/api/chat';

async function sendRealMessage(message) {
    try {
        const response = await fetch(API_BASE, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                model_id: localStorage.getItem('selectedModelId') || 'shizuku',
                voice_id: localStorage.getItem('selectedVoiceId') || 'zh-CN-XiaoxiaoNeural'
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let aiResponse = '';
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            aiResponse += chunk;
            
            // 实时更新打字机效果
            const contentDiv = document.querySelector('.ai-message:last-child .message-content');
            if (contentDiv) {
                contentDiv.textContent = aiResponse;
            }
        }
        
        return aiResponse;
    } catch (error) {
        console.error('AI API调用失败:', error);
        return '抱歉，我遇到了技术问题，请稍后再试。';
    }
}

// 替换演示函数为实际函数
function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;
    
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    messageDiv.innerHTML = `<div class="message-content">${message}</div>`;
    chatMessages.appendChild(messageDiv);
    
    input.value = '';
    
    // 调用实际AI API
    sendRealMessage(message).then(aiResponse => {
        handleAIResponse(aiResponse);
    });
}
