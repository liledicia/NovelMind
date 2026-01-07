"""
API路由 - 小说搜索和推荐
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from typing import Optional
import logging
import requests

from ..schemas.novel import NovelResponse, NovelStats, NovelDetail
from ..schemas.recommendation import RecommendationResponse
from ...services.novel_service import search_novel_exact, insert_novel
from ...services.crawler_service import JinjiangCrawler, NovelNotFoundException, CrawlerException
from ...services.recommendation_service import get_recommendation_summary


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["novels"])


@router.get("/novels/search", response_model=dict)
async def search_novel(q: str = Query(..., min_length=1, description="搜索关键词")):
    """
    搜索小说

    流程：
    1. 先在数据库中精确搜索
    2. 如果未找到，则调用爬虫实时爬取
    3. 返回小说完整信息

    Args:
        q: 小说名称

    Returns:
        {
            "success": true,
            "data": {小说详细信息},
            "stats": {统计数据},
            "source": "database" | "crawled"
        }
    """
    logger.info(f"搜索小说: {q}")

    # Step 1: 在数据库中搜索
    novel_data = search_novel_exact(q)

    if novel_data:
        logger.info(f"从数据库找到小说: {q}")

        # 分离统计数据
        stats_data = {
            "review_count": novel_data.get("review_count"),
            "favorite_count": novel_data.get("favorite_count"),
            "nutrient_count": novel_data.get("nutrient_count"),
            "total_click_count": novel_data.get("total_click_count"),
            "score": novel_data.get("score")
        }

        # 添加原网站链接
        novel_data["url"] = f"https://www.jjwxc.net/onebook.php?novelid={novel_data['book_id']}"

        return {
            "success": True,
            "data": novel_data,
            "stats": stats_data,
            "source": "database"
        }

    # Step 2: 数据库未找到，尝试爬取
    logger.info(f"数据库未找到，开始爬取: {q}")

    try:
        crawler = JinjiangCrawler()
        crawled_data = crawler.crawl_novel_complete(q)

        # 入库
        logger.info(f"爬取成功，准备入库: {crawled_data.get('title')}")
        insert_result = insert_novel(crawled_data)

        if not insert_result:
            logger.warning("小说数据入库失败，但仍返回爬取结果")

        # 分离统计数据
        stats_data = {
            "review_count": crawled_data.get("review_count"),
            "favorite_count": crawled_data.get("favorite_count"),
            "nutrient_count": crawled_data.get("nutrient_count"),
            "total_click_count": crawled_data.get("total_click_count"),
            "score": crawled_data.get("score")
        }

        # 添加原网站链接
        crawled_data["url"] = f"https://www.jjwxc.net/onebook.php?novelid={crawled_data['book_id']}"

        return {
            "success": True,
            "data": crawled_data,
            "stats": stats_data,
            "source": "crawled"
        }

    except NovelNotFoundException:
        logger.error(f"未找到小说: {q}")
        raise HTTPException(status_code=404, detail=f"未找到小说: {q}")

    except CrawlerException as e:
        logger.error(f"爬虫错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"爬取失败: {str(e)}")

    except Exception as e:
        logger.error(f"未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/recommendations/{book_id}", response_model=dict)
async def get_recommendations(
    book_id: int,
    limit: int = Query(default=10, ge=1, le=50, description="推荐数量")
):
    """
    获取小说推荐

    Args:
        book_id: 目标小说ID
        limit: 推荐数量 (1-50)

    Returns:
        {
            "success": true,
            "data": {
                "target_novel": {目标小说信息},
                "recommendations": [{推荐列表}]
            }
        }
    """
    logger.info(f"获取推荐: book_id={book_id}, limit={limit}")

    try:
        result = get_recommendation_summary(book_id, limit)

        return {
            "success": True,
            "data": result
        }

    except ValueError as e:
        logger.error(f"小说ID不存在: {book_id}")
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        logger.error(f"推荐计算错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"推荐计算失败: {str(e)}")


@router.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "NovelMind API"}


@router.get("/proxy/image")
async def proxy_image(url: str = Query(..., description="图片URL")):
    """
    图片代理接口 - 解决外部图床的CORS问题

    通过后端转发外部图片，避免浏览器CORS限制

    Args:
        url: 要代理的图片URL

    Returns:
        图片二进制数据
    """
    try:
        # 只允许代理特定域名的图片（安全考虑）
        allowed_domains = [
            'sinaimg.cn',
            'jjwxc.net',
            'bmp.ovh',
            'loli.net',
            'jd.com',
            'huluxia.com',
            'bdstatic.com'
        ]

        # 检查URL是否来自允许的域名
        if not any(domain in url for domain in allowed_domains):
            raise HTTPException(status_code=403, detail="不支持的图片域名")

        # 请求外部图片
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'https://www.jjwxc.net/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status()

        # 返回图片
        return Response(
            content=response.content,
            media_type=response.headers.get('Content-Type', 'image/jpeg'),
            headers={
                'Cache-Control': 'public, max-age=86400',  # 缓存1天
                'Access-Control-Allow-Origin': '*'  # 允许跨域
            }
        )

    except requests.RequestException as e:
        logger.error(f"图片代理失败: {url}, 错误: {str(e)}")
        raise HTTPException(status_code=404, detail="图片加载失败")

    except Exception as e:
        logger.error(f"图片代理错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器错误")
