"""
YouTube 内容获取器
使用 yt-dlp 替代 pytubefix，解决 visitor-id 和 po-token 问题
"""

import re
import time
import asyncio
import logging
import os
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path

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
        """获取 yt-dlp 配置选项 - 使用 bgutil Script 模式"""
        opts = {
            'quiet': not settings.YOUTUBE_DEBUG,  # 根据调试配置决定是否安静
            'no_warnings': not settings.YOUTUBE_DEBUG,  # 根据调试配置决定是否显示警告
            'extract_flat': False,
            'writeinfojson': False,
            'writethumbnail': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'skip_download': True,  # 只获取信息，不下载视频
            'ignoreerrors': False,
        }
        
        # 如果启用调试模式，添加详细输出
        if settings.YOUTUBE_DEBUG:
            opts.update({
                'verbose': True,  # 添加详细输出
                'debug_printtraffic': True,  # 打印网络流量调试信息
            })
            logger.info("YouTube 调试模式已启用")
        
        # 配置代理
        if settings.USE_PROXY and settings.PROXY_URL:
            opts['proxy'] = settings.PROXY_URL
            logger.info("为 yt-dlp 配置代理: %s", settings.PROXY_URL)
        
        # 配置 cookies
        if settings.YOUTUBE_USE_COOKIES and settings.YOUTUBE_COOKIES_FILE:
            if os.path.exists(settings.YOUTUBE_COOKIES_FILE):
                opts['cookiefile'] = settings.YOUTUBE_COOKIES_FILE
                logger.info(f"使用 cookies 文件: {settings.YOUTUBE_COOKIES_FILE}")
            else:
                logger.warning(f"Cookies 文件不存在: {settings.YOUTUBE_COOKIES_FILE}")
        
        # 配置 bgutil-ytdlp-pot-provider Script 模式
        # 这个插件会自动检测 Node.js 并生成 PO Token，无需额外服务
        try:
            # 检查 Node.js 是否可用
            import subprocess
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                node_version = result.stdout.strip()
                logger.info(f"检测到 Node.js: {node_version}")
                logger.info("bgutil-ytdlp-pot-provider 将使用 Script 模式自动生成 PO Token")
            else:
                logger.warning("未检测到 Node.js，PO Token 生成可能受限")
        except Exception as e:
            logger.warning(f"Node.js 检测失败: {str(e)}，PO Token 生成可能受限")
        
        # 使用官方推荐的 mweb 客户端配置
        # bgutil-ytdlp-pot-provider 插件会自动为 mweb 客户端生成 PO Token
        opts['extractor_args'] = {
            'youtube': {
                'player_client': ['mweb'],  # 使用移动网页客户端
                'player_skip': ['configs'],  # 跳过配置获取
                # 插件会自动添加 po_token 参数，无需手动配置
            }
        }
        
        # 设置用户代理为移动浏览器
        opts['http_headers'] = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
        }
        
        logger.info("yt-dlp 配置: 使用 mweb 客户端 + bgutil Script 模式 PO Token 支持")
        
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
            
            # 提取视频 ID 用于诊断
            video_id = None
            if 'youtube.com/watch?v=' in url:
                video_id = url.split('v=')[1].split('&')[0]
            elif 'youtu.be/' in url:
                video_id = url.split('youtu.be/')[1].split('?')[0]
            
            logger.info(f"开始提取视频信息，视频ID: {video_id}")
            
            # 详细打印 yt-dlp 配置参数
            logger.info("=== yt-dlp 详细配置参数 ===")
            logger.info(f"代理设置: {opts.get('proxy', 'None')}")
            logger.info(f"客户端配置: {opts.get('extractor_args', {})}")
            logger.info(f"HTTP 头部: {opts.get('http_headers', {})}")
            logger.info(f"安静模式: {opts.get('quiet', False)}")
            logger.info(f"详细模式: {opts.get('verbose', False)}")
            logger.info(f"调试流量: {opts.get('debug_printtraffic', False)}")
            
            # 环境检查
            logger.info("=== 环境检查 ===")
            
            # 检查 Node.js
            try:
                import subprocess
                node_result = subprocess.run(['node', '--version'], 
                                           capture_output=True, text=True, timeout=5)
                if node_result.returncode == 0:
                    logger.info(f"✅ Node.js 版本: {node_result.stdout.strip()}")
                else:
                    logger.error("❌ Node.js 不可用")
            except Exception as node_error:
                logger.error(f"❌ Node.js 检查失败: {str(node_error)}")
            
            # 检查 bgutil 包
            try:
                bgutil_result = subprocess.run(['pip3', 'show', 'bgutil-ytdlp-pot-provider'], 
                                             capture_output=True, text=True, timeout=5)
                if bgutil_result.returncode == 0:
                    logger.info("✅ bgutil-ytdlp-pot-provider 包已安装")
                    # 提取版本信息
                    for line in bgutil_result.stdout.split('\n'):
                        if line.startswith('Version:'):
                            logger.info(f"版本: {line.strip()}")
                        elif line.startswith('Location:'):
                            logger.info(f"位置: {line.strip()}")
                else:
                    logger.error("❌ bgutil-ytdlp-pot-provider 包未安装")
            except Exception as bgutil_error:
                logger.error(f"❌ bgutil 包检查失败: {str(bgutil_error)}")
            
            # 检查 yt-dlp 插件目录
            try:
                import site
                site_packages = site.getsitepackages()
                logger.info(f"Python site-packages 路径: {site_packages}")
                
                # 查找 yt_dlp_plugins 目录
                for path in site_packages:
                    plugins_path = Path(path) / 'yt_dlp_plugins'
                    if plugins_path.exists():
                        logger.info(f"✅ 找到 yt-dlp 插件目录: {plugins_path}")
                        plugins = list(plugins_path.glob('*'))
                        logger.info(f"插件目录内容: {[p.name for p in plugins]}")
                        break
                else:
                    logger.warning("⚠️ 未找到 yt_dlp_plugins 目录")
                    
            except Exception as plugins_error:
                logger.error(f"❌ 插件目录检查失败: {str(plugins_error)}")
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                logger.info("使用 yt-dlp 提取视频信息")
                
                # 检查 yt-dlp 版本
                logger.info(f"yt-dlp 版本: {yt_dlp.version.__version__}")
                
                # 检查是否有 bgutil 插件相关的信息
                try:
                    # 尝试获取 YouTube extractor 的详细信息
                    youtube_ie = ydl.get_info_extractor('Youtube')
                    if youtube_ie:
                        logger.info(f"YouTube extractor 类: {type(youtube_ie).__name__}")
                        
                        # 检查是否有 PO Token 相关的属性或方法
                        po_token_methods = [method for method in dir(youtube_ie) if 'token' in method.lower()]
                        if po_token_methods:
                            logger.info(f"✅ YouTube extractor PO Token 方法: {po_token_methods}")
                        else:
                            logger.warning("⚠️ YouTube extractor 不支持 PO Token 生成")
                            
                        # 检查客户端配置
                        if hasattr(youtube_ie, '_client_name'):
                            logger.info(f"当前客户端名称: {getattr(youtube_ie, '_client_name', 'Unknown')}")
                            
                except Exception as extractor_error:
                    logger.warning(f"无法获取 YouTube extractor 详细信息: {str(extractor_error)}")
                
                # 尝试先获取基本信息
                try:
                    logger.info("=== 开始第一次提取尝试 ===")
                    info = ydl.extract_info(url, download=False)
                    logger.info("✅ 成功获取视频基本信息")
                    
                    # 打印获取到的关键信息
                    if info:
                        logger.info(f"获取到的标题: {info.get('title', 'N/A')}")
                        logger.info(f"获取到的作者: {info.get('uploader', 'N/A')}")
                        logger.info(f"获取到的时长: {info.get('duration', 'N/A')}")
                        
                        # 检查是否有 PO Token 相关的信息
                        info_str = str(info)
                        if 'po_token' in info_str.lower():
                            logger.info("✅ 响应中包含 PO Token 信息")
                        else:
                            logger.info("⚠️ 响应中未发现 PO Token 信息")
                            
                        if 'visitor_data' in info_str.lower():
                            logger.info("✅ 响应中包含 Visitor Data 信息")
                        else:
                            logger.info("⚠️ 响应中未发现 Visitor Data 信息")
                    
                    return info
                    
                except Exception as extract_error:
                    error_msg = str(extract_error)
                    logger.error(f"=== 第一次提取失败 ===")
                    logger.error(f"错误消息: {error_msg}")
                    
                    # 详细分析错误类型
                    if "Failed to extract any player response" in error_msg:
                        logger.error("🔍 检测到 'Failed to extract any player response' 错误")
                        logger.error("这通常表示:")
                        logger.error("1. PO Token 未生成或无效")
                        logger.error("2. Visitor Data 缺失")
                        logger.error("3. 客户端配置不正确")
                        logger.error("4. IP 被 YouTube 标记")
                        logger.error("5. bgutil 插件未正确工作")
                        
                        # 检查 bgutil 插件是否正常工作
                        logger.info("=== 检查 bgutil 插件状态 ===")
                        
                        # 检查 yt-dlp 是否检测到 bgutil 插件
                        logger.info("检查 yt-dlp 调试输出中的 bgutil 信息...")
                        logger.info("如果看到类似 '[youtube] [pot] PO Token Providers: bgutil:...' 的信息，说明插件已加载")
                        logger.info("如果看到 'bgutil:script-1.1.0 (external, unavailable)' 说明 Script 模式不可用")
                        logger.info("如果看到 'bgutil:http-1.1.0 (external)' 说明 HTTP 模式可用")
                        
                    # 如果失败，尝试不同的客户端配置
                    logger.info("=== 尝试使用备用配置 ===")
                    
                    # 备用配置：使用 web 客户端
                    backup_opts = opts.copy()
                    backup_opts['extractor_args'] = {
                        'youtube': {
                            'player_client': ['web'],
                            'player_skip': ['configs'],
                        }
                    }
                    
                    logger.info("尝试使用 web 客户端配置")
                    logger.info(f"备用配置: {backup_opts.get('extractor_args', {})}")
                    
                    with yt_dlp.YoutubeDL(backup_opts) as backup_ydl:
                        try:
                            info = backup_ydl.extract_info(url, download=False)
                            logger.info("✅ 使用备用配置成功获取视频信息")
                            return info
                        except Exception as backup_error:
                            logger.error(f"备用配置也失败: {str(backup_error)}")
                            
                            # 最后尝试：使用最小配置
                            logger.info("=== 尝试使用最小配置 ===")
                            minimal_opts = {
                                'quiet': False,
                                'no_warnings': False,
                                'skip_download': True,
                                'verbose': True,
                            }
                            
                            if settings.USE_PROXY and settings.PROXY_URL:
                                minimal_opts['proxy'] = settings.PROXY_URL
                                logger.info(f"最小配置中包含代理: {settings.PROXY_URL}")
                            
                            logger.info(f"最小配置参数: {minimal_opts}")
                            
                            with yt_dlp.YoutubeDL(minimal_opts) as minimal_ydl:
                                info = minimal_ydl.extract_info(url, download=False)
                                logger.info("✅ 使用最小配置成功获取视频信息")
                                return info
                
        except DownloadError as e:
            error_msg = str(e)
            logger.error(f"=== yt-dlp 下载错误 ===")
            logger.error(f"错误详情: {error_msg}")
            
            # 检查是否是 PO Token 相关错误
            if "Failed to extract any player response" in error_msg:
                logger.error("🚨 确认为 PO Token 相关错误！")
                logger.error("可能的原因:")
                logger.error("1. bgutil-ytdlp-pot-provider 插件未正确工作")
                logger.error("2. Node.js 版本不兼容（需要 >= 18.0）")
                logger.error("3. 网络环境或代理问题")
                logger.error("4. YouTube 检测并阻止了请求")
                logger.error("5. 容器环境中的依赖缺失")
                
                # 提供解决建议
                logger.error("=== 解决建议 ===")
                logger.error("1. 检查容器中是否安装了 Node.js >= 18.0")
                logger.error("2. 确认 bgutil-ytdlp-pot-provider 包已正确安装")
                logger.error("3. 检查 yt-dlp 插件目录是否存在")
                logger.error("4. 尝试重新构建 Docker 镜像")
                logger.error("5. 检查网络连接和代理设置")
            
            return None
        except ExtractorError as e:
            logger.error(f"yt-dlp 提取器错误: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"yt-dlp 未知错误: {str(e)}")
            logger.error(f"错误类型: {type(e).__name__}")
            import traceback
            logger.error(f"完整错误堆栈: {traceback.format_exc()}")
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

