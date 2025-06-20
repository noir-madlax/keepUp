"""
YouTube 内容获取器
使用 yt-dlp 替代 pytubefix，解决 visitor-id 和 po-token 问题
"""

import re
import time
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime

import yt_dlp
from yt_dlp.utils import DownloadError, ExtractorError

from .base import ContentFetcher, VideoInfo
from app.config import settings
from app.utils.decorators import retry_decorator
from app.models.request import FetchRequest
from app.models.author import AuthorInfo

logger = logging.getLogger(__name__)


class YouTubeFetcher(ContentFetcher):
    """YouTube 视频信息获取器，使用 yt-dlp"""
    
    def __init__(self):
        super().__init__()
        self.platform = "YouTube"
    
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
            transcript = await self._get_transcript(url)
            
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
    
    async def get_author_info(self, url: str) -> Optional[AuthorInfo]:
        """获取作者信息"""
        try:
            logger.info(f"开始获取YouTube作者信息: {url}")
            
            # 在线程池中运行 yt-dlp
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(
                None, 
                self._extract_info_sync, 
                url
            )
            
            if not info:
                logger.error("无法获取视频信息以提取作者信息")
                return None
            
            # 提取作者信息
            author_name = info.get('uploader', '') or info.get('channel', '') or '未知作者'
            author_icon = ''
            
            # 尝试获取作者头像
            thumbnails = info.get('thumbnails', [])
            if thumbnails:
                author_icon = thumbnails[0].get('url', '')
            
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
            
            # 在线程池中运行 yt-dlp
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(
                None, 
                self._extract_info_sync, 
                url
            )
            
            if not info:
                logger.error("无法获取视频信息以提取章节信息")
                return None
            
            # 提取章节信息
            chapters = info.get('chapters', [])
            if not chapters:
                logger.info("该视频没有章节信息")
                return None
            
            # 格式化章节信息
            chapter_lines = []
            for i, chapter in enumerate(chapters, 1):
                title = chapter.get('title', f'章节 {i}')
                start_time = chapter.get('start_time', 0)
                end_time = chapter.get('end_time', 0)
                
                # 转换时间格式
                start_min, start_sec = divmod(int(start_time), 60)
                end_min, end_sec = divmod(int(end_time), 60)
                
                chapter_line = f"{i}. {title} ({start_min:02d}:{start_sec:02d} - {end_min:02d}:{end_sec:02d})"
                chapter_lines.append(chapter_line)
            
            chapters_text = "\n".join(chapter_lines)
            logger.info(f"成功获取章节信息，共 {len(chapters)} 个章节")
            
            return chapters_text
            
        except Exception as e:
            logger.error(f"获取YouTube章节信息失败: {str(e)}")
            return None
    
    async def _get_transcript(self, url: str) -> Optional[str]:
        """获取视频转录/字幕"""
        try:
            # 这里可以集成 youtube-transcript-api 或其他字幕获取方法
            # 目前返回 None，表示暂未实现
            logger.info("字幕获取功能暂未实现")
            return None
            
        except Exception as e:
            logger.error(f"获取字幕失败: {str(e)}")
            return None
    
    def _get_ydl_opts(self) -> Dict[str, Any]:
        """获取 yt-dlp 配置选项 - 支持 bgutil PO Token provider"""
        opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'writeinfojson': False,
            'writethumbnail': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'skip_download': True,  # 只获取信息，不下载视频
            'ignoreerrors': False,
            # 配置推荐的客户端和 PO Token 支持
            'extractor_args': {
                'youtube': {
                    'player_client': ['default', 'mweb'],  # 使用官方推荐的 mweb 客户端
                }
            }
        }
        
        # 配置代理
        if settings.USE_PROXY and settings.PROXY_URL:
            opts['proxy'] = settings.PROXY_URL
            logger.info("为 yt-dlp 配置代理: %s", settings.PROXY_URL)
        
        # 检查 bgutil provider 是否可用
        try:
            import requests
            import os
            
            # 优先使用环境变量中的 bgutil provider URL（docker-compose 环境）
            bgutil_url = os.getenv('BGUTIL_PROVIDER_URL', 'http://localhost:4416')
            
            response = requests.get(f"{bgutil_url}/health", timeout=2)
            if response.status_code == 200:
                logger.info(f"bgutil PO Token provider 服务可用: {bgutil_url}")
                # bgutil-ytdlp-pot-provider 插件会自动处理 PO Token
                # 不需要手动配置，插件会自动与 provider 服务通信
            else:
                logger.warning(f"bgutil provider 服务不可用: {bgutil_url}，将使用默认配置")
        except Exception as e:
            logger.warning(f"无法连接到 bgutil provider: {str(e)}，将使用默认配置")
        
        logger.info("yt-dlp 配置完成，支持 PO Token 和 mweb 客户端")
        return opts

    @retry_decorator()
    async def get_video_info(self, url: str) -> Optional[VideoInfo]:
        """获取YouTube视频信息"""
        try:
            logger.info(f"开始获取YouTube视频信息: {url}")
            start_time = time.time()
            
            # 在线程池中运行 yt-dlp（因为它是同步的）
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(
                None, 
                self._extract_info_sync, 
                url
            )
            
            if not info:
                logger.error("无法获取视频信息")
                return None
            
            # 转换为 VideoInfo 格式
            video_info = self._convert_to_video_info(info)
            
            elapsed_time = time.time() - start_time
            logger.info(f"成功获取视频信息，耗时: {elapsed_time:.2f}秒")
            
            return video_info
            
        except Exception as e:
            logger.error(f"获取YouTube视频信息失败: {str(e)}")
            return None
    
    def _extract_info_sync(self, url: str) -> Optional[Dict[str, Any]]:
        """同步提取视频信息"""
        try:
            opts = self._get_ydl_opts()
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                logger.info("使用 yt-dlp 提取视频信息")
                info = ydl.extract_info(url, download=False)
                return info
                
        except DownloadError as e:
            logger.error(f"yt-dlp 下载错误: {str(e)}")
            return None
        except ExtractorError as e:
            logger.error(f"yt-dlp 提取器错误: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"yt-dlp 未知错误: {str(e)}")
            return None

    def _convert_to_video_info(self, info: Dict[str, Any]) -> VideoInfo:
        """将 yt-dlp 的信息转换为 VideoInfo 格式"""
        try:
            # 基本信息
            title = info.get('title', '未知标题')
            description = info.get('description', '')
            author = info.get('uploader', '') or info.get('channel', '') or '未知作者'
            
            # 缩略图
            thumbnail_url = ''
            thumbnails = info.get('thumbnails', [])
            if thumbnails:
                # 选择最高质量的缩略图
                thumbnail_url = thumbnails[-1].get('url', '')
            
            # 作者头像
            author_icon = ''
            if thumbnails:
                author_icon = thumbnails[0].get('url', '')
            
            # 发布日期
            publish_date = None
            upload_date = info.get('upload_date')
            if upload_date:
                try:
                    # upload_date 格式通常是 YYYYMMDD
                    publish_date = datetime.strptime(upload_date, '%Y%m%d')
                except (ValueError, TypeError):
                    logger.warning(f"无法解析发布日期: {upload_date}")
            
            # 时长（秒）
            duration = info.get('duration', 0) or 0
            
            # 观看次数
            views = info.get('view_count', 0) or 0
            
            # 频道ID
            channel_id = info.get('channel_id', '') or info.get('uploader_id', '')
            
            logger.info(f"成功转换视频信息: {title}")
            
            return VideoInfo(
                title=title,
                description=description,
                author=author,
                author_icon=author_icon,
                thumbnail=thumbnail_url,
                publish_date=publish_date,
                duration=duration,
                views=views,
                channel_id=channel_id
            )
            
        except Exception as e:
            logger.error(f"转换视频信息时出错: {str(e)}")
            # 返回基本信息，避免完全失败
            return VideoInfo(
                title=info.get('title', '未知标题'),
                description='',
                author=info.get('uploader', '未知作者'),
                author_icon='',
                thumbnail='',
                publish_date=None,
                duration=0,
                views=0,
                channel_id=''
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

