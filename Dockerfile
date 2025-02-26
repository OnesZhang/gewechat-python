# 使用Python 3.9作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置Python环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 安装依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Start of Selection
# 复制requirements.txt并安装Python依赖，使用清华源
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --timeout=120
# End of Selection

# 复制项目文件
COPY . .

# 确保entrypoint.sh是可执行的
RUN chmod +x entrypoint.sh

# 设置入口点
ENTRYPOINT ["/app/entrypoint.sh"] 