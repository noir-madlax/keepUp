from typing import Optional, Dict, List
from .base import ContentFetcher, VideoInfo
from app.models.article import ArticleCreate
import re
from app.config import settings
from youtube_transcript_api import YouTubeTranscriptApi
import json
from app.utils.logger import logger
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pytubefix import YouTube

class YouTubeFetcher(ContentFetcher):
    def __init__(self):
        # 保留现有的代理配置
        self.proxies = None
        if settings.USE_PROXY and settings.PROXY_URL:
            self.proxies = {
                'http': settings.PROXY_URL,
                'https': settings.PROXY_URL
            }
    
    def can_handle(self, url: str) -> bool:
        """检查是否是 YouTube URL"""
        youtube_patterns = [
            r'youtube\.com/watch\?v=[\w-]+',
            r'youtu\.be/[\w-]+'
        ]
        return any(re.search(pattern, url) for pattern in youtube_patterns)
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """从 URL 中提取视频 ID"""
        patterns = [
            r'youtube\.com/watch\?v=([\w-]+)',  # 标准 YouTube URL
            r'youtu\.be/([\w-]+)',              # 短 URL
            r'youtube\.com/embed/([\w-]+)',      # 嵌入式 URL
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    async def fetch(self, url: str) -> Optional[str]:
        """获取 YouTube 视频内容并格式化字幕"""
        try:
            logger.info(f"获取 YouTube 内容: {url}")
            logger.info(f"当前代理配置: {self.proxies}")
            
            # 提取视频 ID
            video_id = self.extract_video_id(url)
            if not video_id:
                logger.error(f"无法从 URL 提取视频 ID: {url}")
                return None

            # 使用代理获取字幕
            logger.info(f"开始获取字幕，代理状态: {'启用' if self.proxies else '禁用'}")
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, proxies=self.proxies)
            
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
            
            logger.info(f"成功格式化视频字幕，总行数: {len(readable_text)}")
            
            return final_content
            
        except Exception as e:
            logger.error(f"获取 YouTube 内容失败: {str(e)}", exc_info=True)
            return None 

    async def get_video_info(self, url: str) -> Optional[VideoInfo]:
        """获取YouTube视频信息"""
        try:
            logger.info(f"开始获取YouTube视频信息: {url}")
            
            # 获取页面内容
            response = requests.get(url, proxies=self.proxies)
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取标题
            title = soup.find('meta', {'name': 'title'})['content']
            logger.info(f"获取到标题: {title}")

            # 提取描述
            description_meta = soup.find('meta', {'name': 'description'})
            description = description_meta['content'] if description_meta else ""
            logger.info(f"获取到描述: {description[:100]}...")  # 只打印前100个字符

            # 提取作者
            author_meta = soup.find('link', {'itemprop': 'name'})
            author_name = author_meta['content'] if author_meta else "未知作者"
            logger.info(f"获取到作者: {author_name}")

            # 提取发布日期
            publish_date_meta = soup.find('meta', {'itemprop': 'datePublished'})
            publish_date = None
            if publish_date_meta and publish_date_meta['content']:
                try:
                    publish_date = datetime.fromisoformat(publish_date_meta['content'].replace('Z', '+00:00'))
                    logger.info(f"获取到发布日期: {publish_date}")
                except ValueError:
                    logger.warning(f"无法解析发布日期: {publish_date_meta['content']}")

            # 构建作者信息
            author = {
                "name": author_name,
                "platform": "YouTube"
            }
            logger.info(f"构建的作者信息: {author}")
            
            # 构建文章信息
            article = ArticleCreate(
                title=title,
                content=description,
                channel="YouTube",
                tags=["视频"],
                original_link=url,
                publish_date=publish_date
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
            return None 

    async def get_chapters(self, url: str) -> Optional[str]:
        """获取YouTube视频章节信息"""
        try:
            logger.info(f"开始获取YouTube视频章节信息: {url}")
            
            # 设置代理
            if self.proxies:
                logger.info("使用代理获取章节信息")
                import pytubefix
                pytubefix.request.core._default_proxy = self.proxies
            
            # 使用 pytubefix 获取视频信息
            yt = YouTube(url)
            
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
            logger.error(f"获取YouTube视频章节信息失败: {str(e)}", exc_info=True)
            return None