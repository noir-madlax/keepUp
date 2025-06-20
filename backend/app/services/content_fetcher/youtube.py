import re
import time
import requests
import os
import random
import json
import subprocess
from typing import Optional, Dict, List
from bs4 import BeautifulSoup
from datetime import datetime
from pytubefix import YouTube, Channel
from youtube_transcript_api import YouTubeTranscriptApi
import traceback

from app.config import settings
from app.utils.decorators import retry_decorator
from app.models.article import ArticleCreate
from app.services.content_fetcher.base import ContentFetcher, VideoInfo, AuthorInfo
from app.utils.logger import logger

class YouTubeFetcher(ContentFetcher):
    def __init__(self):
        # 保留现有的代理配置
        self.proxies = None
        
        # 添加visitor ID缓存
        self._visitor_id = None
        self._visitor_id_timestamp = None
        self._visitor_id_cache_duration = 3600  # 1小时缓存
        
        # 添加 po_token 缓存
        self._po_token = None
        self._po_token_timestamp = None
        self._po_token_cache_duration = 1800  # 30分钟缓存
        
        # 设置证书环境变量 - 这可能会解决SSL问题
        os.environ['REQUESTS_CA_BUNDLE'] = ''
        os.environ['CURL_CA_BUNDLE'] = ''

    def can_handle(self, url: str) -> bool:
        """检查是否是 YouTube URL"""
        youtube_patterns = [
            r'youtube\.com/watch\?v=[\w-]+',
            r'youtu\.be/[\w-]+',
            r'youtube\.com/live/[\w-]+'  # 2024-03-19: 添加对直播链接的支持
        ]
        return any(re.search(pattern, url) for pattern in youtube_patterns)
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """从 URL 中提取视频 ID"""
        patterns = [
            r'youtube\.com/watch\?v=([\w-]+)',  # 标准 YouTube URL
            r'youtu\.be/([\w-]+)',              # 短 URL
            r'youtube\.com/embed/([\w-]+)',      # 嵌入式 URL
            r'youtube\.com/live/([\w-]+)'        # 2024-03-19: 添加对直播链接的支持
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    async def get_proxy(self) -> Optional[Dict[str, str]]:
        """获取代理配置"""
        if not settings.USE_PROXY:
            return None
        
        # 这里应该从代理池中获取可用代理
        # 暂时返回配置的代理
        return {
            'http': settings.PROXY_URL,
            'https': settings.PROXY_URL
        }

    def get_realistic_headers(self, include_visitor_id: str = None) -> Dict[str, str]:
        """生成真实的浏览器headers"""
        # 随机选择一个真实的User-Agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Sec-CH-UA': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-CH-UA-Mobile': '?0',
            'Sec-CH-UA-Platform': '"Windows"'
        }
        
        # 如果有visitor ID，添加相关headers
        if include_visitor_id:
            headers['x-goog-visitor-id'] = include_visitor_id
            headers['Cookie'] = f'VISITOR_INFO1_LIVE={include_visitor_id}'
        
        return headers

    async def get_visitor_id(self, proxies: Optional[Dict[str, str]] = None) -> Optional[str]:
        """获取YouTube visitor ID"""
        try:
            # 检查缓存
            current_time = time.time()
            if (self._visitor_id and self._visitor_id_timestamp and 
                current_time - self._visitor_id_timestamp < self._visitor_id_cache_duration):
                logger.info("使用缓存的visitor ID")
                return self._visitor_id

            logger.info("开始获取YouTube visitor ID")
            
            # 创建session并设置完整的浏览器headers
            session = requests.Session()
            headers = self.get_realistic_headers()
            session.headers.update(headers)
            
            # 访问YouTube首页获取visitor ID
            response = session.get('https://www.youtube.com', proxies=proxies, timeout=30, verify=False)
            response.raise_for_status()
            
            # 从cookies中提取VISITOR_INFO1_LIVE
            visitor_cookie = None
            for cookie in session.cookies:
                if cookie.name == 'VISITOR_INFO1_LIVE':
                    visitor_cookie = cookie.value
                    break
            
            if visitor_cookie:
                self._visitor_id = visitor_cookie
                self._visitor_id_timestamp = current_time
                logger.info(f"成功获取visitor ID: {visitor_cookie[:10]}...")
                return visitor_cookie
            else:
                logger.warning("未能从cookies中找到VISITOR_INFO1_LIVE")
                # 尝试从页面内容中提取
                try:
                    # 查找页面中的visitor ID
                    import re
                    visitor_match = re.search(r'"VISITOR_DATA":"([^"]+)"', response.text)
                    if visitor_match:
                        visitor_data = visitor_match.group(1)
                        self._visitor_id = visitor_data
                        self._visitor_id_timestamp = current_time
                        logger.info(f"从页面内容获取visitor ID: {visitor_data[:10]}...")
                        return visitor_data
                except Exception as e:
                    logger.warning(f"从页面内容提取visitor ID失败: {str(e)}")
                
                return None
                
        except Exception as e:
            logger.error(f"获取visitor ID失败: {str(e)}")
            return None

    def create_enhanced_session(self, visitor_id: str = None, proxies: Dict[str, str] = None) -> requests.Session:
        """创建增强的requests session"""
        session = requests.Session()
        
        # 设置完整的浏览器headers
        headers = self.get_realistic_headers(visitor_id)
        session.headers.update(headers)
        
        # 设置代理
        if proxies:
            session.proxies.update(proxies)
        
        # 设置SSL验证
        session.verify = False
        
        # 设置超时
        session.timeout = 30
        
        return session

    @retry_decorator()
    async def fetch(self, url: str) -> Optional[str]:
        """获取YouTube视频字幕"""
        try:
            logger.info(f"开始获取YouTube内容: {url}")
            
            # 提取视频ID
            video_id = self.extract_video_id(url)
            if not video_id:
                logger.error("无法从URL中提取视频ID")
                return None
            
            start_time = time.time()
            success = False
            proxies = None
            
            try:
                # 获取代理配置
                if settings.USE_PROXY:
                    proxies = await self.get_proxy()
                    logger.info("使用代理获取字幕")
                
                # 获取visitor ID
                visitor_id = await self.get_visitor_id(proxies)
                
                # 尝试使用增强的方式获取字幕
                if visitor_id:
                    logger.info("使用visitor ID和完整浏览器伪装获取字幕")
                    transcript_list = await self._get_transcript_with_enhanced_headers(video_id, visitor_id, proxies)
                else:
                    logger.info("使用标准方式获取字幕")
                    # 使用原有方式
                    if settings.USE_PROXY:
                        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, proxies=proxies)
                    else:
                        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                
                if not transcript_list:
                    raise ValueError("No video transcript found")
                success = True
            finally:
                pass

            # 格式化字幕内容
            readable_text = []
            for entry in transcript_list:
                # 将时间戳（秒）转换为时:分:秒格式
                start_time = float(entry['start'])
                hours = int(start_time // 3600)
                minutes = int((start_time % 3600) // 60)
                seconds = int(start_time % 60)
                
                # 添加格式化的文本行
                formatted_line = f"[{hours:02}:{minutes:02}:{seconds:02}] {entry['text']}"
                readable_text.append(formatted_line)
            
            # 将所有行组合成最终文本
            final_content = "\n".join(readable_text)
            
            if not final_content:
                raise ValueError("No video transcript content found")
            
            logger.info(f"成功格式化视频字幕，总行数: {len(readable_text)}")

            return final_content
            
        except Exception as e:
            logger.error(f"获取 YouTube 内容失败: {str(e)}", exc_info=True)
            raise e

    async def _get_transcript_with_enhanced_headers(self, video_id: str, visitor_id: str, proxies: Optional[Dict[str, str]] = None):
        """使用增强headers获取字幕"""
        try:
            # 首先尝试使用原有API，但使用增强的session
            try:
                from youtube_transcript_api._transcripts import TranscriptListFetcher
                
                # 创建增强的session
                session = self.create_enhanced_session(visitor_id, proxies)
                
                # 使用自定义session创建TranscriptListFetcher
                fetcher = TranscriptListFetcher(session)
                transcript_list = fetcher.fetch(video_id)
                
                # 查找字幕
                try:
                    # 优先查找英文字幕
                    transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
                    return transcript.fetch()
                except:
                    # 如果没有英文字幕，尝试获取任何可用的字幕
                    available_transcripts = list(transcript_list._manually_created_transcripts.keys()) or list(transcript_list._generated_transcripts.keys())
                    if available_transcripts:
                        transcript = transcript_list.find_transcript([available_transcripts[0]])
                        return transcript.fetch()
                    else:
                        raise ValueError("No transcripts available")
                        
            except Exception as api_error:
                logger.warning(f"使用增强headers的API调用失败: {str(api_error)}")
                
                # 如果上述方法失败，回退到标准API
                logger.info("回退到标准API调用")
                if proxies:
                    return YouTubeTranscriptApi.get_transcript(video_id, proxies=proxies)
                else:
                    return YouTubeTranscriptApi.get_transcript(video_id)
                
        except Exception as e:
            logger.error(f"使用增强headers获取字幕失败: {str(e)}")
            raise e

    @retry_decorator()
    async def get_video_info(self, url: str) -> Optional[VideoInfo]:
        """获取YouTube视频信息"""
        try:
            logger.info(f"开始获取YouTube视频信息: {url}")

            start_time = time.time()
            success = False
            
            try:
                # 获取代理配置
                if settings.USE_PROXY:
                    proxies = await self.get_proxy()
                    logger.info("使用代理获取视频信息,proxies: %s", proxies)
                else:
                    proxies = None
                
                # 先尝试生成 po_token
                logger.info("尝试生成 po_token")
                token_info = await self.generate_po_token()
                
                if token_info:
                    # 使用预生成的 po_token
                    logger.info("使用预生成的 po_token 创建 YouTube 客户端")
                    yt = YouTube(
                        url, 
                        use_po_token=True,
                        po_token_verifier=(token_info['visitor_data'], token_info['po_token']),
                        proxies=proxies
                    )
                else:
                    # 回退到 WEB 客户端
                    logger.info("po_token 生成失败，尝试使用 'WEB' 客户端")
                    yt = YouTube(url, 'WEB', proxies=proxies)
                
                # 直接使用pytubefix的内置属性获取信息
                title = yt.title or "未知视频标题"
                logger.info(f"✅ 通过pytubefix获取到标题: {title}")
                
                description = yt.description or ""
                logger.info(f"✅ 通过pytubefix获取到描述: {len(description)} 字符")
                
                author = yt.author or "未知作者"
                logger.info(f"✅ 通过pytubefix获取到作者: {author}")
                
                # 获取缩略图URL
                thumbnail_url = yt.thumbnail_url or ""
                logger.info(f"✅ 通过pytubefix获取到缩略图: {thumbnail_url}")
                
                # 获取发布日期
                publish_date = None
                try:
                    if yt.publish_date:
                        publish_date = yt.publish_date
                        logger.info(f"✅ 通过pytubefix获取到发布日期: {publish_date}")
                except Exception as e:
                    logger.warning(f"获取发布日期失败: {e}")
                
                # 获取视频时长
                length = None
                try:
                    if hasattr(yt, 'length') and yt.length:
                        length = yt.length
                        logger.info(f"✅ 通过pytubefix获取到视频时长: {length} 秒")
                except Exception as e:
                    logger.warning(f"获取视频时长失败: {e}")
                
                # 获取观看次数
                views = None
                try:
                    if hasattr(yt, 'views') and yt.views:
                        views = yt.views
                        logger.info(f"✅ 通过pytubefix获取到观看次数: {views}")
                except Exception as e:
                    logger.warning(f"获取观看次数失败: {e}")
                
                # 获取频道ID
                channel_id = None
                try:
                    if hasattr(yt, 'channel_id') and yt.channel_id:
                        channel_id = yt.channel_id
                        logger.info(f"✅ 通过pytubefix获取到频道ID: {channel_id}")
                except Exception as e:
                    logger.warning(f"获取频道ID失败: {e}")

                # 尝试获取作者头像URL - 这个可能需要特殊处理
                author_icon = ""
                try:
                    # 如果有频道ID，可以构造头像URL
                    if channel_id:
                        # YouTube频道头像的标准URL格式
                        author_icon = f"https://yt3.ggpht.com/ytc/channel/{channel_id}"
                        logger.info(f"✅ 构造作者头像URL: {author_icon}")
                except Exception as e:
                    logger.warning(f"获取作者头像失败: {e}")

                success = True
                elapsed_time = time.time() - start_time
                logger.info(f"✅ YouTube视频信息获取成功，耗时: {elapsed_time:.2f}秒")

                return VideoInfo(
                    title=title,
                    description=description,
                    author=author,
                    author_icon=author_icon,
                    thumbnail=thumbnail_url,
                    publish_date=publish_date,
                    duration=length,
                    views=views,
                    channel_id=channel_id
                )

            except Exception as e:
                logger.warning(f"主要方案失败: {str(e)}")
                # 备用方案：尝试另一种方式
                try:
                    if not token_info:
                        # 如果之前没有生成 po_token，现在尝试生成
                        logger.info("尝试生成 po_token 作为备用方案")
                        token_info = await self.generate_po_token()
                    
                    if token_info:
                        logger.info("使用 po_token 备用方案")
                        yt = YouTube(
                            url, 
                            use_po_token=True,
                            po_token_verifier=(token_info['visitor_data'], token_info['po_token']),
                            proxies=proxies
                        )
                    else:
                        logger.info("最后尝试：使用 use_po_token=True（交互式）")
                        yt = YouTube(url, use_po_token=True, proxies=proxies)
                    
                    title = yt.title or "未知视频标题"
                    description = yt.description or ""
                    author = yt.author or "未知作者"
                    thumbnail_url = yt.thumbnail_url or ""
                    
                    # 获取其他元数据
                    publish_date = None
                    try:
                        if yt.publish_date:
                            publish_date = yt.publish_date
                    except Exception:
                        pass
                    
                    length = None
                    try:
                        if hasattr(yt, 'length') and yt.length:
                            length = yt.length
                    except Exception:
                        pass
                    
                    views = None
                    try:
                        if hasattr(yt, 'views') and yt.views:
                            views = yt.views
                    except Exception:
                        pass
                    
                    channel_id = None
                    try:
                        if hasattr(yt, 'channel_id') and yt.channel_id:
                            channel_id = yt.channel_id
                    except Exception:
                        pass
                    
                    author_icon = ""
                    try:
                        if channel_id:
                            author_icon = f"https://yt3.ggpht.com/ytc/channel/{channel_id}"
                    except Exception:
                        pass
                    
                    success = True
                    elapsed_time = time.time() - start_time
                    logger.info(f"✅ 备用方案成功获取YouTube视频信息，耗时: {elapsed_time:.2f}秒")
                    
                    return VideoInfo(
                        title=title,
                        description=description,
                        author=author,
                        author_icon=author_icon,
                        thumbnail=thumbnail_url,
                        publish_date=publish_date,
                        duration=length,
                        views=views,
                        channel_id=channel_id
                    )
                    
                except Exception as fallback_error:
                    logger.error(f"所有备用方案都失败: {str(fallback_error)}")
                    logger.error(f"原始错误: {str(e)}")
                    logger.error(f"错误详情: {traceback.format_exc()}")
                    return None

        except Exception as e:
            logger.error(f"YouTube视频信息获取过程异常: {e}")
            return None

    async def get_chapters(self, url: str) -> Optional[str]:
        """获取YouTube视频章节信息"""
        try:
            logger.info("开始获取YouTube视频章节信息")
            
            # 获取代理配置
            if settings.USE_PROXY:
                proxies = await self.get_proxy()
                logger.info("使用代理获取章节信息")
            else:
                proxies = None
            
            # 使用pytubefix的'WEB'客户端自动生成po_token获取章节信息
            logger.info("使用pytubefix 'WEB'客户端获取章节信息")
            yt = YouTube(url, 'WEB', proxies=proxies)
            
            # 直接使用pytubefix的内置chapters属性
            chapters = yt.chapters
            
            if not chapters:
                logger.info("该视频没有章节信息")
                return None
            
            logger.info(f"✅ 通过pytubefix获取到 {len(chapters)} 个章节")
            
            # 格式化章节信息
            chapters_text = []
            for i, chapter in enumerate(chapters):
                # pytubefix的Chapter对象有title和start_seconds属性
                start_time = chapter.start_seconds if hasattr(chapter, 'start_seconds') else 0
                title = chapter.title if hasattr(chapter, 'title') else f"章节 {i+1}"
                
                # 将秒数转换为时分秒格式
                hours = int(start_time // 3600)
                minutes = int((start_time % 3600) // 60)
                seconds = int(start_time % 60)
                
                if hours > 0:
                    time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                else:
                    time_str = f"{minutes:02d}:{seconds:02d}"
                
                chapters_text.append(f"{time_str} - {title}")
                logger.info(f"章节 {i+1}: {time_str} - {title}")
            
            result = "\n".join(chapters_text)
            logger.info(f"✅ 章节信息格式化完成")
            return result
            
        except Exception as e:
            logger.warning(f"'WEB'客户端获取章节失败: {str(e)}")
            # 备用方案：使用use_po_token=True
            try:
                logger.info("尝试备用方案获取章节: use_po_token=True")
                yt = YouTube(url, use_po_token=True, proxies=proxies)
                
                chapters = yt.chapters
                
                if not chapters:
                    logger.info("该视频没有章节信息")
                    return None
                
                logger.info(f"✅ 通过备用方案获取到 {len(chapters)} 个章节")
                
                # 格式化章节信息
                chapters_text = []
                for i, chapter in enumerate(chapters):
                    start_time = chapter.start_seconds if hasattr(chapter, 'start_seconds') else 0
                    title = chapter.title if hasattr(chapter, 'title') else f"章节 {i+1}"
                    
                    # 将秒数转换为时分秒格式
                    hours = int(start_time // 3600)
                    minutes = int((start_time % 3600) // 60)
                    seconds = int(start_time % 60)
                    
                    if hours > 0:
                        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    else:
                        time_str = f"{minutes:02d}:{seconds:02d}"
                    
                    chapters_text.append(f"{time_str} - {title}")
                
                result = "\n".join(chapters_text)
                logger.info(f"✅ 备用方案章节信息格式化完成")
                return result
                
            except Exception as fallback_error:
                logger.warning(f"备用方案也失败: {str(fallback_error)}")
                logger.warning(f"原始错误: {str(e)}")
                logger.warning(f"错误详情: {traceback.format_exc()}")
                return None

    async def get_author_info(self, url: str) -> Optional[AuthorInfo]:
        """获取 YouTube 作者信息"""
        pass

    async def generate_po_token(self) -> Optional[Dict[str, str]]:
        """使用 youtube-po-token-generator 生成 po_token"""
        try:
            # 检查缓存
            current_time = time.time()
            if (self._po_token and self._po_token_timestamp and 
                current_time - self._po_token_timestamp < self._po_token_cache_duration):
                logger.info("使用缓存的 po_token")
                return self._po_token

            logger.info("开始生成新的 po_token")
            
            # 设置代理环境变量（如果使用代理）
            env = os.environ.copy()
            if settings.USE_PROXY:
                env['HTTPS_PROXY'] = settings.PROXY_URL
                env['HTTP_PROXY'] = settings.PROXY_URL
                logger.info("为 po_token 生成设置代理环境变量")
            
            # 调用 youtube-po-token-generator
            result = subprocess.run(
                ['youtube-po-token-generator'],
                capture_output=True,
                text=True,
                timeout=30,
                env=env
            )
            
            if result.returncode == 0:
                # 解析 JSON 输出
                token_data = json.loads(result.stdout.strip())
                visitor_data = token_data.get('visitorData')
                po_token = token_data.get('poToken')
                
                if visitor_data and po_token:
                    token_info = {
                        'visitor_data': visitor_data,
                        'po_token': po_token
                    }
                    
                    # 缓存 token
                    self._po_token = token_info
                    self._po_token_timestamp = current_time
                    
                    logger.info(f"✅ 成功生成 po_token: visitorData={visitor_data[:10]}..., poToken={po_token[:10]}...")
                    return token_info
                else:
                    logger.error("po_token 生成器返回了无效数据")
                    return None
            else:
                logger.error(f"po_token 生成失败: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("po_token 生成超时")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"解析 po_token 输出失败: {e}")
            return None
        except Exception as e:
            logger.error(f"生成 po_token 时发生异常: {e}")
            return None

