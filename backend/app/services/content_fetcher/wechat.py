"""
微信文章内容获取器
使用极致了API获取微信公众号文章内容
"""

import requests
import json
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from .base import ContentFetcher, VideoInfo
from app.config import settings
from app.utils.decorators import retry_decorator
from app.models.request import FetchRequest
from app.models.author import AuthorInfo
from app.models.article import ArticleCreate

logger = logging.getLogger(__name__)


class WeChatFetcher(ContentFetcher):
    """微信文章内容获取器，使用极致了API"""
    
    def __init__(self):
        super().__init__()
        self.platform = "WeChat"
        self.api_url = "https://www.dajiala.com/fbmain/monitor/v3/article_detail"
        self.api_key = getattr(settings, 'DAJIALA_KEY', None)
        self.verify_code = getattr(settings, 'DAJIALA_VERIFYCODE', None)
        
        if not self.api_key or not self.verify_code:
            logger.warning("DAJIALA_KEY 或 DAJIALA_VERIFYCODE 未配置")
    
    def can_handle(self, url: str) -> bool:
        """检查是否可以处理该URL"""
        return 'mp.weixin.qq.com' in url
    
    async def fetch(self, url: str, request: Optional[FetchRequest] = None) -> Optional[str]:
        """获取微信文章内容"""
        try:
            logger.info(f"开始获取微信文章内容: {url}")
            
            # 获取视频信息（复用get_video_info，避免重复API调用）
            video_info = await self.get_video_info(url)
            if not video_info:
                logger.error("无法获取文章信息")
                return None
            
            # 组合内容
            content_parts = [
                f"标题: {video_info.title}",
                f"作者: {video_info.author.get('name', '')}",
                f"描述: {video_info.description}",
            ]
            
            # 添加文章内容
            if video_info.article.content:
                content_parts.append(f"正文内容: {video_info.article.content}")
            
            content = "\n\n".join(content_parts)
            logger.info(f"成功获取微信文章内容，长度: {len(content)}")
            
            return content
            
        except Exception as e:
            logger.error(f"获取微信文章内容失败: {str(e)}")
            return None
    
    async def _get_article_detail(self, url: str) -> Optional[Dict[str, Any]]:
        """调用极致了API获取文章详情"""
        if not self.api_key or not self.verify_code:
            logger.error("API密钥或验证码未配置")
            return None
        
        try:
            headers = {
                'Content-Type': 'application/json'
            }
            
            data = {
                "url": url,
                "key": self.api_key,
                "mode": 2,  # 纯文字+富文本格式
                "verifycode": self.verify_code
            }
            
            # 在线程池中执行HTTP请求
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(self.api_url, headers=headers, json=data, timeout=30)
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:  # 成功
                    logger.info(f"成功获取微信文章详情: {url}")
                    return result
                else:
                    logger.error(f"API返回错误: {result.get('code')} - {self._get_error_message(result.get('code'))}")
                    return None
            else:
                logger.error(f"HTTP请求失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"调用极致了API失败: {str(e)}")
            return None
    
    def _get_error_message(self, code: int) -> str:
        """获取错误信息"""
        error_map = {
            101: "文章被删除或违规或公众号已迁移",
            105: "文章解析失败",
            106: "文章解析失败", 
            107: "解析失败，请重试"
        }
        return error_map.get(code, "未知错误")
    
    @retry_decorator()
    async def get_video_info(self, url: str) -> Optional[VideoInfo]:
        """获取微信文章基础信息"""
        try:
            logger.info(f"开始获取微信文章基础信息: {url}")
            
            # 调用极致了API获取文章详情
            article_data = await self._get_article_detail(url)
            if not article_data:
                logger.error("无法获取文章详情")
                return None
            
            # 提取基础信息
            title = article_data.get('title', '未知标题')
            desc = article_data.get('desc', '')
            content = article_data.get('content', '')
            
            # 作者信息
            author_name = article_data.get('nick_name', '未知公众号')
            author_icon = ''  # 微信API不提供头像
            
            # 发布时间
            publish_date = self._parse_publish_date(article_data.get('pubtime', ''))
            
            # 构建author字典
            author = {
                'name': author_name,
                'icon': author_icon,
                'platform': 'WeChat'
            }
            
            # 构建ArticleCreate对象
            article = ArticleCreate(
                title=title,
                content=content,
                channel="wechat",
                tags=["微信文章", "公众号"],
                original_link=url,
                publish_date=publish_date,
                cover_image_url=''  # 微信文章暂不处理封面图片
            )
            
            logger.info(f"成功获取微信文章基础信息: {title}")
            
            return VideoInfo(
                title=title,
                description=desc,
                author=author,
                article=article
            )
            
        except Exception as e:
            logger.error(f"获取微信文章基础信息失败: {str(e)}")
            return None
    
    def _parse_publish_date(self, date_str: str) -> Optional[datetime]:
        """解析发布时间"""
        if not date_str:
            return None
        
        try:
            # 微信API返回格式: 2025-06-27 18:33:48
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except Exception as e:
            logger.warning(f"解析发布时间失败: {date_str}, 错误: {str(e)}")
            return None
    
    async def get_author_info(self, url: str) -> Optional[AuthorInfo]:
        """获取作者信息"""
        try:
            logger.info(f"开始获取微信文章作者信息: {url}")
            
            # 调用极致了API获取文章详情
            article_data = await self._get_article_detail(url)
            if not article_data:
                logger.error("无法获取文章详情以提取作者信息")
                return None
            
            # 提取作者信息
            author_name = article_data.get('nick_name', '未知公众号')
            
            author_info = AuthorInfo(
                name=author_name,
                icon='',  # 微信API不提供头像
                platform="WeChat"
            )
            
            logger.info(f"成功获取微信文章作者信息: {author_name}")
            return author_info
            
        except Exception as e:
            logger.error(f"获取微信文章作者信息失败: {str(e)}")
            return None
    
    async def get_chapters(self, url: str) -> Optional[str]:
        """获取章节信息"""
        try:
            logger.info(f"开始获取微信文章章节信息: {url}")
            
            # 微信文章通常没有章节概念，返回None
            logger.info("微信文章不支持章节信息获取")
            return None
            
        except Exception as e:
            logger.error(f"获取微信文章章节信息失败: {str(e)}")
            return None 