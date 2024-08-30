# 使用官方 Python 镜像作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制项目的 requirements 文件并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件到工作目录
COPY . .

# 设置环境变量（可选）
ENV PYTHONUNBUFFERED=1

# 启动应用
CMD ["python", "main.py"]
