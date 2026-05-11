#!/bin/bash
echo "🏯 灵山胜境 AI数字人导游 - 环境安装"
echo "===================================="

# 1. 检查 Python
python3 --version || { echo "请先安装 Python 3.10+"; exit 1; }

# 2. 创建虚拟环境
cd backend
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install fastapi uvicorn websockets python-multipart dashscope openai
pip install chromadb langchain langchain-community langchain-text-splitters
pip install funasr modelscope
pip install edge-tts
pip install python-dotenv pydantic

# 4. 安装系统依赖
sudo apt install -y ffmpeg espeak 2>/dev/null || echo "请手动安装 ffmpeg"

echo ""
echo "✅ 安装完成！"
echo ""
echo "▶️ 启动方法："
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   export DASHSCOPE_API_KEY='sk-你的key'"
echo "   python3 main.py"
echo ""
echo "🌐 浏览器打开: http://localhost:8000"
