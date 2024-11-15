from abc import ABC, abstractmethod
from typing import Optional

class ContentFetcher(ABC):
    """内容获取器的基类"""
    
    @abstractmethod
    async def fetch(self, url: str) -> Optional[str]:
        """获取内容的抽象方法"""
        pass
    
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """判断是否可以处理该 URL"""
        pass 