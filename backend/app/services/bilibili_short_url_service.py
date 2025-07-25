"""
B站短链接转换服务
参考 https://api.suyanw.cn/api/bilibili_short_url.php 的实现
"""

import requests
import re
from typing import Optional
from urllib.parse import urlencode, quote
from app.utils.logger import logger

class BilibiliShortUrlService:
    """B站短链接转换服务"""
    
    def __init__(self):
        self.short_url_api = "https://api.suyanw.cn/api/bilibili_short_url.php"
        self.timeout = 10
    
    def is_bilibili_url(self, url: str) -> bool:
        """判断是否为B站链接"""
        bilibili_patterns = [
            r'bilibili\.com/video/BV[\w]+',      # 标准BV号链接
            r'bilibili\.com/video/av\d+',        # 旧的AV号链接
            r'b23\.tv/[\w]+',                    # B站短链接
            r'm\.bilibili\.com/video/[\w]+',     # 手机端链接
            r'www\.bilibili\.com/video/[\w]+',   # 完整域名链接
        ]
        return any(re.search(pattern, url, re.IGNORECASE) for pattern in bilibili_patterns)
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """从B站链接中提取视频ID"""
        # 匹配BV号
        bv_match = re.search(r'BV([\w]+)', url, re.IGNORECASE)
        if bv_match:
            return f"BV{bv_match.group(1)}"
        
        # 匹配AV号
        av_match = re.search(r'av(\d+)', url, re.IGNORECASE)
        if av_match:
            return f"av{av_match.group(1)}"
        
        return None
    
    def normalize_bilibili_url(self, url: str) -> str:
        """标准化B站链接格式"""
        # 如果已经是短链接，直接返回
        if 'b23.tv' in url:
            return url
        
        # 提取视频ID
        video_id = self.extract_video_id(url)
        if not video_id:
            return url
        
        # 标准化为完整格式
        return f"https://www.bilibili.com/video/{video_id}"
    
    async def convert_to_short_url(self, url: str) -> Optional[str]:
        """
        将B站链接转换为短链接
        
        Args:
            url: B站视频链接
            
        Returns:
            短链接或None（如果转换失败）
        """
        if not self.is_bilibili_url(url):
            logger.warning(f"不是有效的B站链接: {url}")
            return None
        
        # 如果已经是短链接，直接返回
        if 'b23.tv' in url:
            logger.info(f"已经是短链接: {url}")
            return url
        
        try:
            # 标准化URL
            normalized_url = self.normalize_bilibili_url(url)
            logger.info(f"标准化B站链接: {url} -> {normalized_url}")
            
            # 调用短链接API
            params = {"url": normalized_url}
            response = requests.get(
                self.short_url_api,
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                short_url = response.text.strip()
                
                # 验证返回的是否为有效的短链接
                if short_url.startswith('https://b23.tv/'):
                    logger.info(f"短链接转换成功: {normalized_url} -> {short_url}")
                    return short_url
                else:
                    logger.warning(f"短链接API返回异常响应: {short_url}")
                    return None
            else:
                logger.error(f"短链接API请求失败: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"短链接API请求异常: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"短链接转换失败: {str(e)}")
            return None
    
    async def batch_convert_to_short_urls(self, urls: list[str]) -> dict[str, Optional[str]]:
        """
        批量转换B站链接为短链接
        
        Args:
            urls: B站视频链接列表
            
        Returns:
            原链接到短链接的映射
        """
        results = {}
        
        for url in urls:
            short_url = await self.convert_to_short_url(url)
            results[url] = short_url
        
        return results
    
    async def resolve_short_url(self, short_url: str) -> Optional[str]:
        """
        解析短链接，获取原始链接
        
        Args:
            short_url: B站短链接
            
        Returns:
            原始链接或None
        """
        if not short_url.startswith('https://b23.tv/'):
            return None
        
        try:
            # 使用HEAD请求获取重定向
            response = requests.head(short_url, allow_redirects=False, timeout=self.timeout)
            
            if response.status_code in [301, 302]:
                redirect_url = response.headers.get('Location', '')
                if 'bilibili.com/video/' in redirect_url:
                    logger.info(f"短链接解析成功: {short_url} -> {redirect_url}")
                    return redirect_url
            
            # 如果HEAD请求失败，尝试GET请求
            response = requests.get(short_url, allow_redirects=True, timeout=self.timeout)
            if 'bilibili.com/video/' in response.url:
                logger.info(f"短链接解析成功: {short_url} -> {response.url}")
                return response.url
                
        except Exception as e:
            logger.warning(f"短链接解析失败: {short_url}, 错误: {str(e)}")
        
        return None 