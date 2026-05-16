#!/bin/bash
# AI Testing 项目 - 初始化脚本
set -e

echo "🚀 AI Testing Project Setup"
echo "=========================="

# 检查 Python
echo "[1/4] 检查 Python..."
python3 --version || { echo "需要 Python 3.10+"; exit 1; }

# 安装依赖
echo "[2/4] 安装 Python 依赖..."
pip install -r requirements.txt -q

# 配置环境
echo "[3/4] 配置环境..."
if [ ! -f .env ]; then
    cp config/env.example .env
    echo "⚠️  请编辑 .env 填写你的 API 密钥"
fi

# Node.js (可选)
if command -v node &> /dev/null; then
    echo "[4/4] 安装 Node.js 依赖..."
    cd mcp-servers/node && npm install && cd ../..
fi

echo ""
echo "✅ 初始化完成！"
echo "运行: python -m pytest tests/ -v"
