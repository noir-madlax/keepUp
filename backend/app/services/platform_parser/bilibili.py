import re
from typing import Optional, Tuple
from .base import PlatformParser
from app.utils.logger import logger
from app.services.bilibili_short_url_service import BilibiliShortUrlService

class BilibiliParser(PlatformParser):
    """B站视频URL解析器"""
    
    def __init__(self):
        self.short_url_service = BilibiliShortUrlService()
    
    def can_handle(self, url: str) -> bool:
        """判断是否为B站视频链接"""
        return self.short_url_service.is_bilibili_url(url)
    
    def extract_bv_id(self, url: str) -> Optional[str]:
        """从URL中提取BV号或AV号，并转换为BV格式"""
        return self.short_url_service.extract_video_id(url)
    
    async def resolve_short_url(self, short_url: str) -> Optional[str]:
        """解析B站短链接，获取真实的视频URL"""
        return await self.short_url_service.resolve_short_url(short_url)

    async def parse(self, url: str) -> Optional[Tuple[str, str, str]]:
        """
        解析B站视频URL并转换为短链接格式
        
        Returns:
            Tuple[str, str, str]: (platform, short_url, original_url)
        """
        if not self.can_handle(url):
            return None
            
        logger.info(f"解析B站视频URL: {url}")
        
        try:
            # 首先统一转换为短链接
            short_url = await self.short_url_service.convert_to_short_url(url)
            if not short_url:
                logger.error(f"无法转换为短链接: {url}")
                # 如果转换失败，采用原有的标准化逻辑作为备用
                processed_url = url
                
                # 处理短链接
                if 'b23.tv' in url:
                    resolved_url = await self.resolve_short_url(url)
                    if resolved_url:
                        processed_url = resolved_url
                    else:
                        logger.error(f"无法解析短链接: {url}")
                        return None
                
                # 提取视频ID
                video_id = self.extract_bv_id(processed_url)
                if not video_id:
                    logger.error(f"无法提取视频ID: {processed_url}")
                    return None
                
                # 标准化URL格式
                standardized_url = f"https://www.bilibili.com/video/{video_id}"
                
                logger.info(f"B站URL标准化完成: {url} -> {standardized_url}")
                return "bilibili", standardized_url, url
            
            logger.info(f"B站URL转换为短链接完成: {url} -> {short_url}")
            return "bilibili", short_url, url
            
        except Exception as e:
            logger.error(f"解析B站URL失败: {str(e)}")
            return None 