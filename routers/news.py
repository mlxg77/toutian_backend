from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud import news
from crud import news_cache
from schemas.news import NewsDetailResponse, NewsListResponse
from utils.response import success_response

# 创建 APIRouter 实例
# prefix 路由前缀（API 接口规范文档）
# tags 分组 标签
router = APIRouter(prefix="/api/news", tags=["news"])

# 接口实现流程
# 1. 模块化路由 → API 接口规范文档
# 2. 定义模型类 → 数据库表（数据库设计文档）
# 3. 在 crud 文件夹里面创建文件，封装操作数据库的方法
# 4. 在路由处理函数里面调用 crud 封装好的方法，响应结果

# 获取新闻分类
@router.get("/categories")
async def get_categories(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    # 先获取数据库里面新闻分类数据 → 先定义模型类 → 封装查询数据的方法
    categories = await news_cache.get_categories(db, skip, limit)
    return success_response(message="获取新闻分类成功", data=categories)

# 获取新闻列表
@router.get("/list")
async def get_news_list(
        category_id: int = Query(..., alias="categoryId"),
        page: int = 1,
        page_size: int = Query(10, alias="pageSize", le=100),
        db: AsyncSession = Depends(get_db)
):
    # 思路：处理分页规则 → 查询新闻列表 → 计算总量 → 计算是否还有更多
    offset = (page - 1) * page_size
    news_list = await news_cache.get_news_list(db, category_id, offset, page_size)
    total = await news_cache.get_news_count(db, category_id)
    # (跳过的 + 当前列表里面的数量) < 总量
    has_more = (offset + len(news_list)) < total
    response_data = NewsListResponse(
        list=news_list,
        total=total,
        has_more=has_more
    )
    return success_response(message="获取新闻列表成功", data=response_data)

# 获取新闻详情
@router.get("/detail")
async def get_news_detail(news_id: int = Query(..., alias="id"), db: AsyncSession = Depends(get_db)):
    # 获取新闻详情 + 浏览量+1 + 相关新闻
    news_detail = await news_cache.get_news_detail(db, news_id) # new_detail ORM 对象和其他的缓存不一样
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")

    views_res = await news.increase_news_views(db, news_detail.id)
    if not views_res:
        raise HTTPException(status_code=404, detail="新闻不存在")

    related_news = await news_cache.get_related_news(db, news_detail.id, news_detail.category_id)

    response_data = NewsDetailResponse.model_validate(news_detail)
    response_data.related_news = related_news
    return success_response(message="success", data=response_data)
