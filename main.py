import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from fastapi import FastAPI
from routers import news, users, favorite, history
from fastapi.middleware.cors import CORSMiddleware

# 日志目录：容器内是 /app/log（docker-compose 把它挂载到宿主机 ./log），
# 本地直接跑时是项目根目录下的 log
LOG_DIR = Path(__file__).parent / "log"
LOG_DIR.mkdir(exist_ok=True)

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s"

# 控制台输出：docker logs / 本地终端都能看到
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# 文件输出：按天滚动，保留 30 天，过期自动删（历史文件形如 app.log.2026-09-05）
file_handler = TimedRotatingFileHandler(
    LOG_DIR / "app.log",
    when="midnight",
    backupCount=30,
    encoding="utf-8",
)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# 同时输出到控制台和文件
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[console_handler, file_handler],
)

# uvicorn 自己的日志（启动/报错/每个请求的访问日志）默认只进控制台，
# 这里换成同一套 handler，让它们也能落盘到 log/app.log；
# propagate=False 切断向父级/root 的传播，否则同一条日志会被重复记录多次
for _name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
    _logger = logging.getLogger(_name)
    _logger.handlers = [console_handler, file_handler]
    _logger.propagate = False

from utils.exception_handlers import register_exception_handlers

app = FastAPI()

# 注册异常处理器
register_exception_handlers(app)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # 允许的源，开发阶段允许所有源，生产环境需要指定源
    allow_credentials=True,  # 允许携带cookie
    allow_methods=["*"],     # 允许的请求方法
    allow_headers=["*"],     # 允许的请求头
)


@app.get("/")
async def root():
    return {"message": "Hello World"}

# 挂载路由/注册路由
app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(history.router)
