from typing import Optional, Tuple
from app.utils.logger import logger
from .platform_parser.base import PlatformParser
from .platform_parser.youtube import YouTubeParser
from .platform_parser.apple import ApplePodcastParser
from .platform_parser.spotify import SpotifyParser
from .platform_parser.webpage import WebPageParser
from .platform_parser.wechat import WeChatParser

class ContentResolver:
    """内容解析服务"""
    
    def __init__(self):
        self.parsers: list[PlatformParser] = [
            WeChatParser(),
            YouTubeParser(),
            ApplePodcastParser(),
            SpotifyParser(),
            WebPageParser()
        ]
    
    async def resolve(self, url: str) -> Optional[Tuple[str, str, str]]:
        """
        解析URL并返回平台信息
        
        Args:
            url: 原始URL
            
        Returns:
            Optional[Tuple[str, str, str]]: (platform, parsed_url, original_url) 或 None
        """
        logger.info(f"开始解析URL: {url}")
        
        for parser in self.parsers:
            if parser.can_handle(url):
                result = await parser.parse(url)
                if result:
                    return result
                    
        logger.warning(f"没有找到合适的析器处理URL: {url}")
        return None 