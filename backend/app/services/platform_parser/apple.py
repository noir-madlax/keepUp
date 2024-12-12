import re
from typing import Optional, Tuple
from .base import PlatformParser
from app.utils.logger import logger
from app.services.podcast_matcher import PodcastMatcher

class ApplePodcastParser(PlatformParser):
    """Apple Podcast URL解析器"""
    
    def can_handle(self, url: str) -> bool:
        return 'podcasts.apple.com' in url
    
    async def parse(self, url: str) -> Optional[Tuple[str, str, str]]:
        """
        解析Apple Podcast URL并查找对应的YouTube URL
        """
        if not self.can_handle(url):
            return None
        
        # return "apple", url, url
            
        logger.info(f"解析Apple Podcast URL: {url}")
        
        try:
            matcher = PodcastMatcher()
            youtube_url = matcher.match_podcast_url(url)
            
            if youtube_url:
                logger.info(f"找到对应的YouTube URL: {youtube_url}")
                return "apple", youtube_url, url
            else:
                logger.warning(f"未找到对应的YouTube URL: {url}")
                return "apple", url, url
                
        except Exception as e:
            logger.error(f"解析Apple Podcast URL失败: {str(e)}")
            return None 