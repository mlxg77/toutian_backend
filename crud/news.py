from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from models.news import News


async def increase_news_views(db: AsyncSession, news_id: int):
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    await db.commit()

    # 更新 → 检查数据库是否真的命中了数据 → 命中了返回True
    return result.rowcount > 0
