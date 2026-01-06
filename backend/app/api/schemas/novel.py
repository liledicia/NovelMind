"""
小说数据模型（Pydantic）
"""
from pydantic import BaseModel, Field
from typing import Optional


class NovelStats(BaseModel):
    """小说统计数据"""
    review_count: Optional[int] = Field(None, description="书评数")
    favorite_count: Optional[int] = Field(None, description="收藏数")
    nutrient_count: Optional[int] = Field(None, description="营养液数")
    total_click_count: Optional[int] = Field(None, description="点击数")
    score: Optional[int] = Field(None, description="积分")


class NovelDetail(BaseModel):
    """小说详细信息"""
    book_id: int = Field(..., description="小说ID")
    title: str = Field(..., description="书名")
    author: Optional[str] = Field(None, description="作者")
    intro: Optional[str] = Field(None, description="简介")
    tags: Optional[str] = Field(None, description="标签")
    main_chars: Optional[str] = Field(None, description="主角")
    support_chars: Optional[str] = Field(None, description="配角")
    other_info: Optional[str] = Field(None, description="其它信息")
    category: Optional[str] = Field(None, description="文章类型")
    perspective: Optional[str] = Field(None, description="作品视角")
    series: Optional[str] = Field(None, description="所属系列")
    status: Optional[str] = Field(None, description="连载状态")
    word_count: Optional[int] = Field(None, description="字数")
    publish_status: Optional[str] = Field(None, description="出版状态")
    sign_status: Optional[str] = Field(None, description="签约状态")
    last_update_time: Optional[str] = Field(None, description="最后更新时间")
    chapter_count: Optional[int] = Field(None, description="章节数")
    url: Optional[str] = Field(None, description="原网站链接")

    class Config:
        from_attributes = True  # 支持从ORM模型创建


class NovelResponse(BaseModel):
    """小说查询响应"""
    success: bool = Field(default=True, description="请求是否成功")
    data: Optional[NovelDetail] = Field(None, description="小说数据")
    stats: Optional[NovelStats] = Field(None, description="统计数据")
    source: Optional[str] = Field(None, description="数据来源: database 或 crawled")
    message: Optional[str] = Field(None, description="消息")


class SearchQuery(BaseModel):
    """搜索请求参数"""
    q: str = Field(..., min_length=1, description="搜索关键词")
