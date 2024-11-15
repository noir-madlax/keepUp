from typing import List, Optional
from .base import ContentFetcher
from .youtube import YouTubeFetcher
from .xiaoyuzhou import XiaoYuZhouFetcher
from app.utils.logger import logger

class ContentFetcherService:
    def __init__(self):
        self.fetchers: List[ContentFetcher] = [
            YouTubeFetcher(),
            XiaoYuZhouFetcher()
        ]
    
    def get_fetcher(self, url: str) -> Optional[ContentFetcher]:
        """获取合适的内容获取器"""
        for fetcher in self.fetchers:
            if fetcher.can_handle(url):
                return fetcher
        return None
    
    async def fetch_content(self, url: str) -> Optional[str]:
        """获取内容"""
        fetcher = self.get_fetcher(url)
        if not fetcher:
            logger.warning(f"未找到合适的内容获取器: {url}")
            return None
            
        try:
            return await fetcher.fetch(url)
        except Exception as e:
            logger.error(f"获取内容失败: {str(e)}", exc_info=True)
            return None 