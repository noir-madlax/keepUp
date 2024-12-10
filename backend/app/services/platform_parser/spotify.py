import re
from typing import Optional, Tuple
from .base import PlatformParser
from app.utils.logger import logger
from app.services.podcast_matcher import PodcastMatcher

class SpotifyParser(PlatformParser):
    """Spotify URL解析器"""
    
    def can_handle(self, url: str) -> bool:
        return 'open.spotify.com' in url
    
    async def parse(self, url: str) -> Optional[Tuple[str, str, str]]:
        """
        解析Spotify URL并查找对应的YouTube URL
        """
        if not self.can_handle(url):
            return None
            
        logger.info(f"解析Spotify URL: {url}")
        
        try:
            matcher = PodcastMatcher()
            youtube_url = matcher.match_podcast_url(url)
            
            if youtube_url:
                logger.info(f"找到对应的YouTube URL: {youtube_url}")
                return "spotify", youtube_url, url
            else:
                logger.warning(f"未找到对应的YouTube URL: {url}")
                return None
                
        except Exception as e:
            logger.error(f"解析Spotify URL失败: {str(e)}")
            return None 