#!/bin/bash
# 🚀 导游AI - 一键自愈启动
set -e
cd "$(dirname "$0")"

echo "🚀 导游AI - 一键启动"
echo "================================"

# 自动修复日志文件
mkdir -p logs
if [ ! -f logs/interactions.json ] || [ ! -s logs/interactions.json ]; then
    echo '[]' > logs/interactions.json
elif ! python3 -c "import json; json.load(open('logs/interactions.json'))" 2>/dev/null; then
    mv logs/interactions.json logs/interactions.json.backup 2>/dev/null || true
    echo '[]' > logs/interactions.json
    echo "✓ 损坏日志已修复"
fi

# 检查 .env
if [ ! -f .env ]; then
    cp .env.template .env
    echo "⚠ 已创建 .env，请编辑填入API密钥: nano .env"
    echo "  然后重新运行: ./start.sh"
    exit 1
fi

echo "✓ 检查完毕，启动服务..."
python3 main.py
