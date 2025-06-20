from abc import ABC, abstractmethod
from typing import Optional, Dict
from pydantic import BaseModel
from datetime import datetime
from app.models.article import ArticleCreate
from app.models.request import FetchRequest
from app.models.author import AuthorInfo

class VideoInfo(BaseModel):
    """视频基本信息"""
    title: str
    description: str
    author: str  # 作者名称
    author_icon: Optional[str] = ""  # 作者头像URL
    thumbnail: Optional[str] = ""  # 缩略图URL
    publish_date: Optional[datetime] = None  # 发布日期
    duration: Optional[int] = None  # 视频时长（秒）
    views: Optional[int] = None  # 观看次数
    channel_id: Optional[str] = None  # 频道ID

    class Config:
        arbitrary_types_allowed = True

class ContentFetcher(ABC):
    """内容获取基类"""
    @abstractmethod
    async def fetch(self, url: str, request: Optional[FetchRequest] = None) -> Optional[str]:
        """获取内容"""
        pass
        
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """检查是否可以处理该URL"""
        pass
        
    @abstractmethod
    async def get_video_info(self, url: str) -> Optional[VideoInfo]:
        """获取视频基本信息"""
        pass

    @abstractmethod
    async def get_chapters(self, url: str) -> Optional[str]:
        """获取视频章节信息"""
        pass

    @abstractmethod
    async def get_author_info(self, url: str) -> Optional[AuthorInfo]:
        """获取作者信息
        
        Args:
            url: 内容的URL
            
        Returns:
            包含作者信息的AuthorInfo对象，如果获取失败则返回None
        """
        pass