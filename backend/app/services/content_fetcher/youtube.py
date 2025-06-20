import re
import time
import requests
import os
import random
import json
from typing import Optional, Dict, List
from bs4 import BeautifulSoup
from datetime import datetime
from pytubefix import YouTube, Channel
from youtube_transcript_api import YouTubeTranscriptApi

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
                # 获取页面内容
                if settings.USE_PROXY:
                    proxies = await self.get_proxy()
                    logger.info("使用代理获取页面内容,proxies: %s", proxies)
                else:
                    proxies = None
                
                # 获取visitor ID并创建增强session
                visitor_id = await self.get_visitor_id(proxies)
                session = self.create_enhanced_session(visitor_id, proxies)
                
                response = session.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                # 提取标题
                title = soup.find('meta', {'name': 'title'})['content']
                if not title:
                    raise ValueError("No video title found")
                success = True
            finally:
                pass

            # 提取描述
            description_meta = soup.find('meta', {'name': 'description'})
            description = description_meta['content'] if description_meta else ""
            logger.info(f"获取到描述: {description[:100]}...")  # 只打印前100个字符

            # 提取作者
            author_meta = soup.find('link', {'itemprop': 'name'})
            author_name = author_meta['content'] if author_meta else "未知作者"
            logger.info(f"获取到作者: {author_name}")

            # 提取缩略图
            thumbnail_meta = soup.find('link', {'rel': 'image_src'})
            thumbnail_url = thumbnail_meta['href'] if thumbnail_meta else "无缩略图"
            logger.info(f"获取到缩略图: {thumbnail_url}")

            # 提取发布日期
            publish_date_meta = soup.find('meta', {'itemprop': 'datePublished'})
            publish_date = None
            if publish_date_meta and publish_date_meta['content']:
                try:
                    publish_date = datetime.fromisoformat(publish_date_meta['content'].replace('Z', '+00:00'))
                    logger.info(f"获取到发布日期: {publish_date}")
                except ValueError:
                    logger.warning(f"无法解析发布日期: {publish_date_meta['content']}")

            # 在提取作者信息后，添加获取作者头像的代码
            author_icon = ""
            try:
                # 准备headers，包含visitor_id
                headers = {}
                if visitor_id:
                    headers = {
                        'x-goog-visitor-id': visitor_id,
                        'Cookie': f'VISITOR_INFO1_LIVE={visitor_id}'
                    }
                
                if settings.USE_PROXY and proxies:
                    logger.info("使用代理和visitor_id获取作者头像")
                    yt = YouTube(url, proxies=proxies, verify=False, headers=headers)
                else:
                    logger.info("使用visitor_id获取作者头像")
                    yt = YouTube(url, headers=headers)
                
                channel = Channel(yt.channel_url)
                author_icon = channel.initial_data.get('metadata', {}).get('channelMetadataRenderer', {}).get('avatar', {}).get('thumbnails', [{}])[0].get('url', '')
                logger.info(f"成功获取到作者头像: {author_icon}")
            except Exception as e:
                logger.warning(f"获取作者头像失败，将使用空值: {str(e)}")
                author_icon = ""

            # 更新作者信息字典
            author = {
                "name": author_name,
                "platform": "YouTube",
                "icon": author_icon  # 添加作者头像
            }
            logger.info(f"构建的作者信息: {author}")
            
            # 构建文章信息
            article = ArticleCreate(
                title=title,
                content=description,
                channel="YouTube",
                tags=["视频"],
                original_link=url,
                publish_date=publish_date,
                cover_image_url=thumbnail_url
            )
            logger.info(f"构建的文章信息: {article.dict()}")

            video_info = VideoInfo(
                title=title,
                description=description,
                author=author,
                article=article
            )
            
            logger.info(f"最终构建的VideoInfo: {video_info.dict()}")
            return video_info

        except Exception as e:
            logger.error(f"获取YouTube视频信息失败: {str(e)}", exc_info=True)
            raise e

    async def get_chapters(self, url: str) -> Optional[str]:
        """获取YouTube视频章节信息"""
        try:
            logger.info(f"开始获取YouTube视频章节信息: {url}")
            
            # 获取代理配置
            proxies = None
            if settings.USE_PROXY:
                logger.info("使用代理获取章节信息")
                proxies = await self.get_proxy()
            
            # 获取visitor_id
            visitor_id = await self.get_visitor_id(proxies)
            
            # 准备headers，包含visitor_id
            headers = {}
            if visitor_id:
                headers = {
                    'x-goog-visitor-id': visitor_id,
                    'Cookie': f'VISITOR_INFO1_LIVE={visitor_id}'
                }
                logger.info(f"使用visitor_id获取章节信息: {visitor_id[:10]}...")
            
            # 创建YouTube对象并获取章节信息
            try:
                if proxies:
                    yt = YouTube(url, proxies=proxies, headers=headers)
                else:
                    yt = YouTube(url, headers=headers)
                
                if not yt.chapters:
                    logger.info("该视频没有章节信息")
                    return None
                
                # 将章节信息转换为格式化的文本
                chapters_text = []
                for chapter in yt.chapters:
                    formatted_line = f"[{chapter.start_label}] {chapter.title}"
                    chapters_text.append(formatted_line)
                
                # 将所有章节组合成最终文本
                final_content = "\n".join(chapters_text)
                
                logger.info(f"成功获取到章节信息，共 {len(chapters_text)} 个章节")
                return final_content
                
            except Exception as e:
                logger.warning(f"获取YouTube视频章节信息失败，将返回空值: {str(e)}")
                return None

        except Exception as e:
            logger.warning(f"获取YouTube视频章节信息过程出错，将返回空值: {str(e)}")
            return None

    async def get_author_info(self, url: str) -> Optional[AuthorInfo]:
        """获取 YouTube 作者信息"""
        pass