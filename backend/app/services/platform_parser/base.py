from abc import ABC, abstractmethod
from typing import Optional, Tuple
from app.utils.logger import logger

class PlatformParser(ABC):
    """平台解析器基类"""
    
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """判断是否可以处理该URL"""
        pass
    
    @abstractmethod
    async def parse(self, url: str) -> Optional[Tuple[str, str, str]]:
        """
        解析URL并返回平台信息
        
        Args:
            url: 原始URL
            
        Returns:
            Optional[Tuple[str, str, str]]: (platform, parsed_url, original_url) 或 None
            - platform: 平台标识(youtube/apple/spotify)
            - parsed_url: 解析后的YouTube URL
            - original_url: 原始输入的URL
        """
        pass 