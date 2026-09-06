# ============================================================
# 阶段 1：构建层（安装依赖，生成干净的 site-packages）
# ============================================================
FROM python:3.11-slim AS builder

WORKDIR /build

# 先把 requirements 单独拷进去，利用 Docker 缓存：
# 依赖没变时，这一层会直接命中缓存，不用重新 pip install
COPY requirements.txt .

# 安装到 /install 目录，后面再拷到运行镜像（避免运行镜像带着 gcc 等构建工具）
# -i 用清华 pip 源，国内服务器下载快 10 倍以上
RUN pip install --no-cache-dir --prefix=/install \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --trusted-host pypi.tuna.tsinghua.edu.cn \
    -r requirements.txt

# ============================================================
# 阶段 2：运行层（尽可能小，只带运行时需要的东西）
# ============================================================
FROM python:3.11-slim

# 时区设置：让日志、datetime.now() 显示北京时间
ENV TZ=Asia/Shanghai \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app

# 把构建阶段装好的依赖拷过来
COPY --from=builder /install /usr/local

# 拷入项目代码（.dockerignore 会过滤掉 .venv、.git、__pycache__ 等）
COPY . .

# FastAPI 监听 8000
EXPOSE 8000

# 启动命令：host=0.0.0.0 允许外部访问；workers=2 起两个进程提高并发
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
