# 灵山胜境 AI数字人导游

## 系统要求
- Python 3.10+
- 8GB+ 内存
- （可选）NVIDIA GPU + CUDA

## 快速开始

### 1. 解压
tar -xzf tour-guide-ai-portable.tar.gz
cd tour-guide-ai

### 2. 安装环境
bash setup.sh

### 3. 配置 API Key
export DASHSCOPE_API_KEY="sk-你的阿里云百炼key"

### 4. 启动
cd backend
source venv/bin/activate
python3 main.py

### 5. 访问
- 游客端: http://localhost:8000
- 管理后台: http://localhost:8000/admin

## 功能
- 🎭 CSS 数字人（僧人造型）
- 💬 文字/语音问答
- 🔊 Edge TTS 自然语音合成
- 🧠 RAG 知识库（灵山胜境资料）
- 📊 管理后台数据大屏
