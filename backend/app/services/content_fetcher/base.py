from abc import ABC, abstractmethod
from typing import Optional, Dict
from pydantic import BaseModel
from app.models.article import ArticleCreate
from app.models.request import FetchRequest

class VideoInfo(BaseModel):
    """视频基本信息"""
    title: str
    description: str
    author: Dict
    article: ArticleCreate

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