#!/bin/bash

# NovelMind 快速启动脚本

echo "======================================"
echo "  NovelMind 后端服务启动脚本"
echo "======================================"
echo ""

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "❌ 未找到虚拟环境，请先创建虚拟环境"
    echo "   运行: python3 -m venv .venv"
    exit 1
fi

# 激活虚拟环境
echo "📦 激活虚拟环境..."
source .venv/bin/activate

# 检查依赖是否安装
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📥 安装后端依赖..."
    cd backend
    pip install -r requirements.txt
    cd ..
fi

# 启动后端服务
echo ""
echo "🚀 启动FastAPI后端服务..."
echo ""
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
