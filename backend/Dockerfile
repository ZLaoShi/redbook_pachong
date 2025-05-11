# 使用官方 Python 运行时作为父镜像
FROM python:3.11.9

# 设置工作目录
WORKDIR /app

# 安装系统依赖 (git 用于某些 pip 安装, ffmpeg 用于音视频处理)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 将依赖文件复制到容器中
COPY requirements.txt .

# 安装项目依赖
# 使用 --no-cache-dir 来减小镜像体积
RUN pip install --no-cache-dir -r requirements.txt

# 将当前目录内容复制到容器的 /app 目录
COPY . .

# 声明应用运行的端口
EXPOSE 8000

# 运行 uvicorn 服务器
# 使用 0.0.0.0 使其可以从外部访问
# 使用 --reload 使其在代码更改时自动重启
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]