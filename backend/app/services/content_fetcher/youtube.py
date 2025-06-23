"""
YouTube 内容获取器
使用 SerpAPI 替代 yt-dlp，解决稳定性问题
"""

import re
import time
import asyncio
import logging
import requests
from typing import Optional, Dict, Any
from datetime import datetime
from urllib.parse import urlparse, parse_qs

from .base import ContentFetcher, VideoInfo
from app.config import settings
from app.utils.decorators import retry_decorator
from app.models.request import FetchRequest
from app.models.author import AuthorInfo
from app.models.article import ArticleCreate

# 字幕获取
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    TRANSCRIPT_AVAILABLE = True
except ImportError:
    TRANSCRIPT_AVAILABLE = False
    logging.warning("youtube-transcript-api not available, transcript feature disabled")

logger = logging.getLogger(__name__)


class YouTubeFetcher(ContentFetcher):
    """YouTube 视频信息获取器，使用 SerpAPI"""
    
    def __init__(self):
        super().__init__()
        self.platform = "YouTube"
        self.serpapi_key = getattr(settings, 'SERPAPI_KEY', None)
        if not self.serpapi_key:
            logger.warning("SERPAPI_KEY not configured")
    
    def can_handle(self, url: str) -> bool:
        """检查是否可以处理该URL"""
        return self.is_supported_url(url)
        
    def is_supported_url(self, url: str) -> bool:
        """检查是否为支持的YouTube URL"""
        youtube_patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/[\w-]+',
            r'(?:https?://)?(?:www\.)?youtube\.com/v/[\w-]+',
            r'(?:https?://)?(?:m\.)?youtube\.com/watch\?v=[\w-]+',
        ]
        
        return any(re.match(pattern, url) for pattern in youtube_patterns)
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """从YouTube URL中提取视频ID"""
        try:
            parsed_url = urlparse(url)
            if parsed_url.hostname in ['youtube.com', 'www.youtube.com', 'm.youtube.com']:
                query_params = parse_qs(parsed_url.query)
                return query_params.get('v', [None])[0]
            elif parsed_url.hostname == 'youtu.be':
                return parsed_url.path[1:]
            elif 'embed' in parsed_url.path:
                return parsed_url.path.split('/')[-1]
            elif '/v/' in parsed_url.path:
                return parsed_url.path.split('/v/')[-1]
            return None
        except Exception as e:
            logger.error(f"提取视频ID失败: {str(e)}")
            return None

    async def fetch(self, url: str, request: Optional[FetchRequest] = None) -> Optional[str]:
        """获取内容"""
        try:
            logger.info(f"开始获取YouTube内容: {url}")
            
            # 获取视频信息
            video_info = await self.get_video_info(url)
            if not video_info:
                logger.error("无法获取视频信息")
                return None
            
            # 尝试获取字幕/转录
            video_id = self._extract_video_id(url)
            transcript = await self._get_transcript(video_id) if video_id else None
            
            # 组合内容
            content_parts = [
                f"标题: {video_info.title}",
                f"作者: {video_info.author}",
                f"描述: {video_info.description}",
            ]
            
            if transcript:
                content_parts.append(f"转录内容: {transcript}")
            
            content = "\n\n".join(content_parts)
            logger.info(f"成功获取YouTube内容，长度: {len(content)}")
            
            return content
            
        except Exception as e:
            logger.error(f"获取YouTube内容失败: {str(e)}")
            return None
    
    async def _get_serpapi_info(self, video_id: str) -> Optional[Dict[str, Any]]:
        """使用SerpAPI获取视频信息"""
        if not self.serpapi_key:
            logger.error("SERPAPI_KEY未配置")
            return None
        
        try:
            url = "https://serpapi.com/search"
            params = {
                'engine': 'youtube_video',
                'v': video_id,
                'api_key': self.serpapi_key
            }
            
            # 在线程池中执行HTTP请求
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(url, params=params, timeout=15)
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"SerpAPI成功获取视频信息: {video_id}")
                return data
            else:
                logger.error(f"SerpAPI请求失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"SerpAPI调用失败: {str(e)}")
            return None

    async def get_author_info(self, url: str) -> Optional[AuthorInfo]:
        """获取作者信息"""
        try:
            logger.info(f"开始获取YouTube作者信息: {url}")
            
            video_id = self._extract_video_id(url)
            if not video_id:
                logger.error("无法提取视频ID")
                return None
            
            # 使用SerpAPI获取信息
            data = await self._get_serpapi_info(video_id)
            if not data:
                logger.error("无法获取视频信息以提取作者信息")
                return None
            
            # 提取作者信息
            channel_info = data.get('channel', {})
            author_name = channel_info.get('name', '未知作者')
            author_icon = channel_info.get('thumbnail', '')
            
            author_info = AuthorInfo(
                name=author_name,
                icon=author_icon,
                platform="YouTube"
            )
            
            logger.info(f"成功获取作者信息: {author_name}")
            return author_info
            
        except Exception as e:
            logger.error(f"获取YouTube作者信息失败: {str(e)}")
            return None
    
    async def get_chapters(self, url: str) -> Optional[str]:
        """获取视频章节信息"""
        try:
            logger.info(f"开始获取YouTube章节信息: {url}")
            
            video_id = self._extract_video_id(url)
            if not video_id:
                logger.error("无法提取视频ID")
                return None
            
            # SerpAPI不提供章节信息，返回None
            logger.info("SerpAPI不支持章节信息获取")
            return None
            
        except Exception as e:
            logger.error(f"获取YouTube章节信息失败: {str(e)}")
            return None
    
    async def _get_transcript(self, video_id: str) -> Optional[str]:
        """获取视频转录/字幕"""
        if not TRANSCRIPT_AVAILABLE:
            logger.warning("youtube-transcript-api不可用，跳过字幕获取")
            return None
        
        if not video_id:
            logger.error("视频ID为空，无法获取字幕")
            return None
        
        try:
            logger.info(f"开始获取YouTube字幕: {video_id}")
            
            # 配置代理
            if settings.USE_PROXY and settings.PROXY_URL:
                logger.info(f"为字幕获取配置代理: {settings.PROXY_URL}")
                # 在线程池中执行字幕获取，使用代理
                loop = asyncio.get_event_loop()
                transcript_list = await loop.run_in_executor(
                    None,
                    lambda: self._get_transcript_with_proxy(video_id, settings.PROXY_URL)
                )
            else:
                logger.info("未配置代理，直接获取字幕")
                # 在线程池中执行字幕获取
                loop = asyncio.get_event_loop()
                transcript_list = await loop.run_in_executor(
                    None,
                    lambda: YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'zh', 'zh-CN', 'auto'])
                )
            
            if transcript_list:
                # 合并字幕文本
                transcript_text = ' '.join([item['text'] for item in transcript_list])
                logger.info(f"成功获取字幕，长度: {len(transcript_text)}")
                return transcript_text
            else:
                logger.info("未找到可用字幕")
                return None
            
        except Exception as e:
            logger.warning(f"获取字幕失败: {str(e)}")
            return None
    
    def _get_transcript_with_proxy(self, video_id: str, proxy_url: str):
        """使用代理获取字幕，使用新版API的正确方式"""
        import requests
        import urllib3
        from youtube_transcript_api.proxies import GenericProxyConfig
        
        try:
            # 禁用SSL警告
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            # 创建自定义的requests Session，禁用SSL验证
            session = requests.Session()
            session.verify = False  # 禁用SSL验证
            session.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            
            # 设置与代理测试代码相同的headers
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
            })
            
            logger.info(f"使用新版API和自定义Session获取字幕: {proxy_url}")
            
            # 使用新版API，传递自定义的http_client
            api = YouTubeTranscriptApi(http_client=session)
            
            # 获取字幕列表
            transcript_list = api.list(video_id)
            
            # 尝试获取字幕（优先级：英文 > 中文 > 自动生成）
            try:
                transcript = transcript_list.find_transcript(['en', 'zh', 'zh-CN'])
            except:
                # 如果找不到手动字幕，尝试自动生成的
                transcript = transcript_list.find_generated_transcript(['en', 'zh', 'zh-CN'])
            
            # 获取字幕内容
            transcript_data = transcript.fetch()
            return transcript_data
            
        except Exception as e:
            logger.error(f"代理字幕获取失败: {str(e)}")
            raise
    
    def _parse_published_date(self, date_str: str) -> Optional[datetime]:
        """解析发布日期"""
        if not date_str:
            return None
        
        try:
            # SerpAPI返回格式如: "Jan 26, 2025"
            return datetime.strptime(date_str, "%b %d, %Y")
        except ValueError:
            try:
                # 尝试其他可能的格式
                return datetime.strptime(date_str, "%B %d, %Y")
            except ValueError:
                logger.warning(f"无法解析发布日期: {date_str}")
                return None
    
    def _extract_channel_id(self, channel_link: str) -> str:
        """从频道链接中提取频道ID"""
        if not channel_link:
            return ''
        
        try:
            # 从链接中提取频道ID
            # 格式: https://www.youtube.com/channel/UCxxxxx
            if '/channel/' in channel_link:
                return channel_link.split('/channel/')[-1]
            return ''
        except Exception:
            return ''

    @retry_decorator()
    async def get_video_info(self, url: str) -> Optional[VideoInfo]:
        """获取YouTube视频信息"""
        try:
            logger.info(f"开始获取YouTube视频信息: {url}")
            start_time = time.time()
            
            video_id = self._extract_video_id(url)
            if not video_id:
                logger.error("无法提取视频ID")
                return None
            
            # 使用SerpAPI获取信息
            data = await self._get_serpapi_info(video_id)
            if not data:
                logger.error("无法获取视频信息")
                return None
            
            # 转换为 VideoInfo 格式
            video_info = self._convert_to_video_info(data, url)
            
            elapsed_time = time.time() - start_time
            logger.info(f"成功获取视频信息，耗时: {elapsed_time:.2f}秒")
            
            return video_info
            
        except Exception as e:
            logger.error(f"获取YouTube视频信息失败: {str(e)}")
            return None

    def _convert_to_video_info(self, data: Dict[str, Any], original_url: str = "") -> VideoInfo:
        """将 SerpAPI 的信息转换为 VideoInfo 格式"""
        try:
            # 基本信息
            title = data.get('title', '未知标题')
            description = data.get('description', {}).get('content', '') if data.get('description') else ''
            
            # 频道/作者信息
            channel_info = data.get('channel', {})
            author_name = channel_info.get('name', '未知作者')
            author_icon = channel_info.get('thumbnail', '')
            channel_id = self._extract_channel_id(channel_info.get('link', ''))
            
            # 缩略图
            thumbnail_url = data.get('thumbnail', '')
            
            # 发布日期
            publish_date = self._parse_published_date(data.get('published_date', ''))
            
            # 构建author字典
            author = {
                'name': author_name,
                'icon': author_icon,
                'channel_id': channel_id
            }
            
            # 构建ArticleCreate对象
            article = ArticleCreate(
                title=title,
                content=description,
                channel="YouTube",
                tags=["视频", "YouTube"],
                original_link=original_url,
                publish_date=publish_date,
                cover_image_url=thumbnail_url
            )
            
            logger.info(f"成功转换视频信息: {title}")
            
            return VideoInfo(
                title=title,
                description=description,
                author=author,
                article=article
            )
            
        except Exception as e:
            logger.error(f"转换视频信息时出错: {str(e)}")
            # 返回基本信息，避免完全失败
            fallback_article = ArticleCreate(
                title=data.get('title', '未知标题'),
                content='',
                channel="YouTube",
                tags=["视频"],
                original_link=original_url,
                publish_date=None,
                cover_image_url=''
            )
            
            return VideoInfo(
                title=data.get('title', '未知标题'),
                description='',
                author={'name': '未知作者', 'icon': '', 'channel_id': ''},
                article=fallback_article
            )
    
    async def get_channel_info(self, url: str) -> Optional[Dict[str, Any]]:
        """获取频道信息（如果需要的话）"""
        # 这个方法保留用于未来可能的扩展
        # 目前只专注于视频信息获取
        logger.info("频道信息获取功能暂未实现")
        return None
                
    async def get_playlist_info(self, url: str) -> Optional[Dict[str, Any]]:
        """获取播放列表信息（如果需要的话）"""
        # 这个方法保留用于未来可能的扩展
        # 目前只专注于视频信息获取
        logger.info("播放列表信息获取功能暂未实现")
        return None

