import re
from typing import Optional, Tuple
from .base import PlatformParser
from app.utils.logger import logger

class BilibiliParser(PlatformParser):
    """B站视频URL解析器"""
    
    def can_handle(self, url: str) -> bool:
        """判断是否为B站视频链接"""
        bilibili_patterns = [
            r'bilibili\.com/video/BV[\w]+',      # 标准BV号链接
            r'bilibili\.com/video/av\d+',        # 旧的AV号链接
            r'b23\.tv/[\w]+',                    # B站短链接
            r'm\.bilibili\.com/video/[\w]+',     # 手机端链接
            r'www\.bilibili\.com/video/[\w]+',   # 完整域名链接
        ]
        return any(re.search(pattern, url, re.IGNORECASE) for pattern in bilibili_patterns)
    
    def extract_bv_id(self, url: str) -> Optional[str]:
        """从URL中提取BV号或AV号，并转换为BV格式"""
        # 匹配BV号
        bv_match = re.search(r'BV([\w]+)', url, re.IGNORECASE)
        if bv_match:
            return f"BV{bv_match.group(1)}"
        
        # 匹配AV号 - 暂时先返回AV号，实际中可能需要转换API
        av_match = re.search(r'av(\d+)', url, re.IGNORECASE)  
        if av_match:
            return f"av{av_match.group(1)}"
            
        return None
    
    async def resolve_short_url(self, short_url: str) -> Optional[str]:
        """解析B站短链接，获取真实的视频URL"""
        import requests
        try:
            # 设置不跟随重定向，获取重定向目标
            response = requests.head(short_url, allow_redirects=False, timeout=10)
            if response.status_code in [301, 302]:
                redirect_url = response.headers.get('Location', '')
                if 'bilibili.com/video/' in redirect_url:
                    logger.info(f"短链接解析成功: {short_url} -> {redirect_url}")
                    return redirect_url
            
            # 如果HEAD请求失败，尝试GET请求
            response = requests.get(short_url, allow_redirects=True, timeout=10)
            if 'bilibili.com/video/' in response.url:
                logger.info(f"短链接解析成功: {short_url} -> {response.url}")
                return response.url
                
        except Exception as e:
            logger.warning(f"短链接解析失败: {short_url}, 错误: {str(e)}")
            
        return None

    async def parse(self, url: str) -> Optional[Tuple[str, str, str]]:
        """
        解析B站视频URL并标准化为统一格式
        
        Returns:
            Tuple[str, str, str]: (platform, standardized_url, original_url)
        """
        if not self.can_handle(url):
            return None
            
        logger.info(f"解析B站视频URL: {url}")
        
        try:
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
            
        except Exception as e:
            logger.error(f"解析B站URL失败: {str(e)}")
            return None 