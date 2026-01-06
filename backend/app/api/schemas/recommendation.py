"""
推荐相关数据模型（Pydantic）
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from .novel import NovelDetail, NovelStats


class RecommendationItem(BaseModel):
    """单个推荐项"""
    book_id: int = Field(..., description="小说ID")
    title: str = Field(..., description="书名")
    author: Optional[str] = Field(None, description="作者")
    intro: Optional[str] = Field(None, description="简介")
    tags: Optional[str] = Field(None, description="标签")
    category: Optional[str] = Field(None, description="文章类型")
    perspective: Optional[str] = Field(None, description="作品视角")
    status: Optional[str] = Field(None, description="连载状态")
    word_count: Optional[int] = Field(None, description="字数")
    similarity_score: float = Field(..., description="相似度分数 (0-100)")
    match_reasons: List[str] = Field(default_factory=list, description="匹配原因列表")
    url: str = Field(..., description="原网站链接")

    # 统计数据
    review_count: Optional[int] = Field(None, description="书评数")
    favorite_count: Optional[int] = Field(None, description="收藏数")
    score: Optional[int] = Field(None, description="积分")


class TargetNovel(BaseModel):
    """目标小说简要信息"""
    book_id: int = Field(..., description="小说ID")
    title: str = Field(..., description="书名")
    author: Optional[str] = Field(None, description="作者")
    category: Optional[str] = Field(None, description="文章类型")
    tags: Optional[str] = Field(None, description="标签")


class RecommendationResponse(BaseModel):
    """推荐响应"""
    success: bool = Field(default=True, description="请求是否成功")
    data: Optional[dict] = Field(None, description="推荐数据")
    message: Optional[str] = Field(None, description="消息")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "target_novel": {
                        "book_id": 912073,
                        "title": "天涯客",
                        "author": "priest",
                        "category": "原创-纯爱-架空历史-爱情",
                        "tags": "强强 江湖 正剧"
                    },
                    "recommendations": [
                        {
                            "book_id": 1673146,
                            "title": "镇魂",
                            "author": "priest",
                            "similarity_score": 75.5,
                            "match_reasons": ["标签匹配度: 60%", "同作者", "完结状态相同"],
                            "url": "https://www.jjwxc.net/onebook.php?novelid=1673146"
                        }
                    ]
                }
            }
        }
