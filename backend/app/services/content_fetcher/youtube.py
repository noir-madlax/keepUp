from .base import ContentFetcher
from typing import Optional
import re
from app.utils.logger import logger
from youtube_transcript_api import YouTubeTranscriptApi
import httpx
from app.config import settings

class YouTubeFetcher(ContentFetcher):
    def __init__(self):
        self.proxies = None
        if settings.USE_PROXY and settings.PROXY_URL:
            self.proxies = {
                'http://': settings.PROXY_URL,
                'https://': settings.PROXY_URL
            }
    
    def can_handle(self, url: str) -> bool:
        """检查是否是 YouTube URL"""
        youtube_patterns = [
            r'youtube\.com/watch\?v=[\w-]+',
            r'youtu\.be/[\w-]+'
        ]
        return any(re.search(pattern, url) for pattern in youtube_patterns)
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """从 URL 中提取视频 ID"""
        patterns = [
            r'youtube\.com/watch\?v=([\w-]+)',  # 标准 YouTube URL
            r'youtu\.be/([\w-]+)',              # 短 URL
            r'youtube\.com/embed/([\w-]+)',      # 嵌入式 URL
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    async def fetch(self, url: str) -> Optional[str]:
        """获取 YouTube 视频内容"""
        try:
            logger.info(f"获取 YouTube 内容: {url}")
            
            # 提取视频 ID
            video_id = self.extract_video_id(url)
            if not video_id:
                logger.error(f"无法从 URL 提取视频 ID: {url}")
                return None
        
            # 使用代理获取字幕
            transcript_list = YouTubeTranscriptApi.get_transcript(
                video_id,
                proxies=self.proxies if settings.USE_PROXY else None
            )
            
            # 使用代理获取视频信息
            async with httpx.AsyncClient(proxies=self.proxies if settings.USE_PROXY else None) as client:
                # 获取视频信息的代码...
                pass
                
            # 将字幕组合成文本
            content = []
            for entry in transcript_list:
                content.append(entry['text'])
            
            full_text = ' '.join(content)
            logger.info(f"成功获取视频字幕，长度: {len(full_text)} 字符")
            
            return full_text
            
        except Exception as e:
            logger.error(f"获取 YouTube 内容失败: {str(e)}", exc_info=True)
            return None 