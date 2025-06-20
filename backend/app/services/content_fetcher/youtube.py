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
from app.core.config import settings
from app.utils.decorators import retry_decorator

logger = logging.getLogger(__name__)


class YouTubeFetcher(ContentFetcher):
    """YouTube 视频信息获取器，使用 yt-dlp"""
    
    def __init__(self):
        super().__init__()
        self.platform = "YouTube"
        
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
    
    def _get_ydl_opts(self) -> Dict[str, Any]:
        """获取 yt-dlp 配置选项"""
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
        }
        
        # 配置代理
        if settings.USE_PROXY and settings.PROXY_URL:
            opts['proxy'] = settings.PROXY_URL
            logger.info("为 yt-dlp 配置代理: %s", settings.PROXY_URL)
        
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
            view_count = info.get('view_count', 0) or 0
            
            # 点赞数
            like_count = info.get('like_count', 0) or 0
            
            # 标签
            tags = info.get('tags', []) or []
            
            # 其他信息
            video_id = info.get('id', '')
            webpage_url = info.get('webpage_url', '')
            
            logger.info(f"成功转换视频信息: {title}")
            
            return VideoInfo(
                title=title,
                description=description,
                author=author,
                thumbnail_url=thumbnail_url,
                publish_date=publish_date,
                duration=duration,
                view_count=view_count,
                like_count=like_count,
                tags=tags,
                platform="YouTube",
                original_url=webpage_url or '',
                video_id=video_id
            )
            
        except Exception as e:
            logger.error(f"转换视频信息时出错: {str(e)}")
            # 返回基本信息，避免完全失败
            return VideoInfo(
                title=info.get('title', '未知标题'),
                description='',
                author=info.get('uploader', '未知作者'),
                thumbnail_url='',
                publish_date=None,
                duration=0,
                view_count=0,
                like_count=0,
                tags=[],
                platform="YouTube",
                original_url='',
                video_id=info.get('id', '')
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

