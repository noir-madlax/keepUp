from typing import Optional, List, Dict
from .youtube import YouTubeFetcher
from .xiaoyuzhou import XiaoYuZhouFetcher
from .base import VideoInfo
from .apple import ApplePodcastFetcher
from .webpage import WebPageFetcher
from .file import FileFetcher
from .wechat import WeChatFetcher
from app.utils.logger import logger
from app.models.request import FetchRequest
from app.models.author import AuthorInfo

class ContentFetcherService:
    """内容获取服务"""
    def __init__(self, request: Optional[FetchRequest] = None):
        self.request = request
        self.fetchers = [
            FileFetcher(),
            WeChatFetcher(),
            YouTubeFetcher(),
            XiaoYuZhouFetcher(),
            ApplePodcastFetcher(),
            WebPageFetcher()
        ]
    
    async def fetch_content(self, url: str) -> Optional[str]:
        """获取内容"""
        try:
            for fetcher in self.fetchers:
                if fetcher.can_handle(url):
                    if isinstance(fetcher, FileFetcher) and self.request and self.request.content:
                        return await fetcher.fetch(url, self.request)
                    return await fetcher.fetch(url)
            return None
        except Exception as e:
            logger.error(f"获取内容失败: {str(e)}", exc_info=True)
            return None

    async def get_video_info(self, url: str) -> Optional[VideoInfo]:
        """获取视频信息"""
        try:
            for fetcher in self.fetchers:
                if fetcher.can_handle(url):
                    return await fetcher.get_video_info(url)
            return None
        except Exception as e:
            logger.error(f"获取视频信息失败: {str(e)}", exc_info=True)
            return None

    async def get_chapters(self, url: str) -> Optional[str]:
        """获取视频章节信息"""
        try:
            for fetcher in self.fetchers:
                if fetcher.can_handle(url):
                    return await fetcher.get_chapters(url)
            return None
        except Exception as e:
            logger.error(f"获取视频章节信息失败: {str(e)}", exc_info=True)
            return None

    async def get_author_info(self, url: str) -> Optional[AuthorInfo]:
        """获取作者信息"""
        try:
            for fetcher in self.fetchers:
                if fetcher.can_handle(url):
                    return await fetcher.get_author_info(url)
            return None
        except Exception as e:
            logger.error(f"获取作者信息失败: {str(e)}", exc_info=True)
            return None 