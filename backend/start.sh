#!/bin/bash

# 启动脚本 - 管理 bgutil provider 容器和主应用

echo "正在启动 keepup-v2 后端服务..."

# 检查是否已有 bgutil-provider 容器在运行
if ! docker ps --format "table {{.Names}}" | grep -q "bgutil-provider"; then
    echo "启动 bgutil-ytdlp-pot-provider 容器..."
    
    # 尝试启动容器，如果失败则记录错误但继续启动主应用
    if docker run --name bgutil-provider -d -p 4416:4416 --init brainicism/bgutil-ytdlp-pot-provider; then
        echo "bgutil-provider 容器启动成功"
        
        # 等待容器启动完成
        echo "等待 bgutil-provider 服务启动..."
        sleep 10
        
        # 检查服务是否可用
        if curl -f http://localhost:4416/health 2>/dev/null; then
            echo "bgutil-provider 服务运行正常"
        else
            echo "警告: bgutil-provider 服务可能未完全启动，但继续启动主应用"
        fi
    else
        echo "警告: 无法启动 bgutil-provider 容器，将在没有 PO Token 支持的情况下运行"
        echo "这可能导致 YouTube 视频获取失败"
    fi
else
    echo "bgutil-provider 容器已在运行"
fi

# 设置环境变量
export BGUTIL_PROVIDER_URL="http://localhost:4416"

# 启动主应用
echo "启动 FastAPI 应用..."
exec uvicorn main:app --host 0.0.0.0 --port 8000