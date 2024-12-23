from typing import Optional, Tuple
from .base import PlatformParser
from app.utils.logger import logger
from app.models.article import ArticleCreate
from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime

class WebPageParser(PlatformParser):
    """通用网页解析器"""
    
    def can_handle(self, url: str) -> bool:
        """检查是否是普通网页URL"""
        # 如果不是其他已知平台的URL,则认为是普通网页
        known_platforms = [
            'youtube.com', 'youtu.be',
            'podcasts.apple.com',
            'open.spotify.com',
            'xiaoyuzhoufm.com'
        ]
        return not any(platform in url for platform in known_platforms)
    
    async def parse(self, url: str) -> Optional[Tuple[str, str, str]]:
        """
        解析网页URL
        Returns:
            Optional[Tuple[str, str, str]]: (platform, parsed_url, original_url)
        """
        if not self.can_handle(url):
            return None
            
        logger.info(f"解析网页URL: {url}")
        
        try:
            # 这里直接返回原URL,因为不需要转换
            return "webpage", url, url
                
        except Exception as e:
            logger.error(f"解析网页URL失败: {str(e)}")
            return None 