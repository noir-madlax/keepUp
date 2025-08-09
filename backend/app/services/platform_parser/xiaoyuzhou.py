from typing import Optional, Tuple
from .base import PlatformParser
from app.utils.logger import logger


class XiaoYuZhouParser(PlatformParser):
    """小宇宙单集URL解析器"""

    def can_handle(self, url: str) -> bool:
        return 'xiaoyuzhoufm.com/episode/' in url

    async def parse(self, url: str) -> Optional[Tuple[str, str, str]]:
        if not self.can_handle(url):
            return None
        logger.info(f"解析小宇宙URL: {url}")
        return ("xiaoyuzhou", url, url)


