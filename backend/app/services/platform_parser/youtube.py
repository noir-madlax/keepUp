import re
from typing import Optional, Tuple
from .base import PlatformParser
from app.utils.logger import logger

class YouTubeParser(PlatformParser):
    """YouTube URL解析器"""
    
    def can_handle(self, url: str) -> bool:
        youtube_patterns = [
            r'youtube\.com/watch\?v=[\w-]+',
            r'youtu\.be/[\w-]+',
            r'youtube\.com/embed/[\w-]+',
            r'youtube\.com/live/[\w-]+'  # 2024-03-19: 添加对直播链接的支持
        ]
        return any(re.search(pattern, url) for pattern in youtube_patterns)
    
    async def parse(self, url: str) -> Optional[Tuple[str, str, str]]:
        """
        解析YouTube URL
        直接返回原URL,因为不需要转换
        """
        if not self.can_handle(url):
            return None
            
        logger.info(f"解析YouTube URL: {url}")
        return "youtube", url, url 