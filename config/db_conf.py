import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

# 加载 .env 文件（如果存在），同时支持系统环境变量覆盖
load_dotenv()

# 数据库URL：优先从环境变量 DATABASE_URL 读取，否则用默认值
# 注意：密码 Root@123456 中的 @ 必须编码为 %40，否则 URL 解析失败
ASYNC_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+aiomysql://root:Root%40123456@159.75.82.153:3306/news_app?charset=utf8mb4"
)

# 创建异步引擎
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",  # 生产环境默认关闭 SQL 日志
    pool_size=10,  # 设置连接池中保持的持久连接数
    max_overflow=20,  # 设置连接池允许创建的额外连接数
    pool_pre_ping=True,  # 取连接前 ping 一下，避免拿到已被 MySQL 踢掉的死连接
    pool_recycle=1800,  # 连接存活超过 30 分钟强制回收，防止 MySQL 默认 8 小时断连
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    # expire_on_commit=False：提交完事务后，还能继续用刚才那个对象里的数据，不会再偷偷去查数据库。
    expire_on_commit=False
)


# 依赖项，用于获取数据库会话
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
