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
            r'youtube\.com/live/[\w-]+',  # 2024-03-19: 添加对直播链接的支持
            r'm\.youtube\.com/watch\?v=[\w-]+'  # 添加对手机端URL的支持
        ]
        return any(re.search(pattern, url) for pattern in youtube_patterns)
    
    async def parse(self, url: str) -> Optional[Tuple[str, str, str]]:
        """
        解析YouTube URL
        将手机端URL转换为PC端URL
        """
        if not self.can_handle(url):
            return None
            
        logger.info(f"解析YouTube URL: {url}")
        
        # 转换手机端URL为PC端URL
        if 'm.youtube.com' in url:
            pc_url = url.replace('m.youtube.com', 'www.youtube.com')
            logger.info(f"将手机端URL转换为PC端URL: {pc_url}")
            return "youtube", url, pc_url
        
        # 处理短链接
        if 'youtu.be' in url:
            video_id = re.search(r'youtu\.be/([\w-]+)', url).group(1)
            pc_url = f"https://www.youtube.com/watch?v={video_id}"
            logger.info(f"将短链接转换为标准URL: {pc_url}")
            return "youtube", url, pc_url
            
        return "youtube", url, url 