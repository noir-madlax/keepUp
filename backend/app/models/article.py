from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ArticleBase(BaseModel):
    """文章基础模型"""
    title: str
    content: str
    author_id: Optional[int] = None
    channel: str = "YouTube"  # 默认渠道
    tags: List[str] = ["视频"]  # 默认标签
    original_link: Optional[str] = None
    publish_date: Optional[datetime] = None

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )

class ArticleCreate(ArticleBase):
    """创建文章时使用的模型"""
    def dict(self, *args, **kwargs):
        d = super().dict(*args, **kwargs)
        # 确保日期被正确序列化
        if d.get('publish_date'):
            d['publish_date'] = d['publish_date'].isoformat()
        return d

class Article(ArticleBase):
    """完整的文章模型"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_id: Optional[str] = None

    class Config:
        from_attributes = True 