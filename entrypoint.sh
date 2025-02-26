#!/bin/bash
set -e

# 等待MySQL服务就绪
echo "等待MySQL服务就绪..."
for i in {1..30}; do
    if nc -z db 3306; then
        echo "MySQL服务已就绪！"
        break
    fi
    echo "等待MySQL服务就绪... $i/30"
    sleep 1
done

# 如果MySQL服务没有在30秒内就绪，则输出错误信息
if ! nc -z db 3306; then
    echo "MySQL服务未就绪，应用无法启动！"
    exit 1
fi

# 创建数据目录
mkdir -p /app/data

# 最后启动应用
echo "启动GeWeChat Python应用..."
python app.py 