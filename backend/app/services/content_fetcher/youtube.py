from typing import Optional, Dict, List
from .base import ContentFetcher, VideoInfo
from app.models.article import ArticleCreate
import re
from app.config import settings
from youtube_transcript_api import YouTubeTranscriptApi
from app.utils.logger import logger
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pytubefix import YouTube
from pytubefix import Channel
from app.utils.decorators import retry_decorator
from app.repositories.proxy import proxy_repository
import time
import ssl

# 取消 SSL 证书验证
ssl._create_default_https_context = ssl._create_unverified_context

class YouTubeFetcher(ContentFetcher):
    def __init__(self):
        # 保留现有的代理配置
        self.proxies = None
        # if settings.USE_PROXY and settings.PROXY_URL:
        #     self.proxies = {
        #         'http': settings.PROXY_URL,
        #         'https': settings.PROXY_URL
        #     }
    
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
        if settings.USE_PROXY:
            return await proxy_repository.get_available_proxy()
        return None


    @retry_decorator()
    async def fetch(self, url: str) -> Optional[str]:
        """获取 YouTube 视频内容并格式化字幕"""
        try:
            logger.info(f"获取 YouTube 内容: {url}")
            
            # 提取视频 ID
            video_id = self.extract_video_id(url)
            if not video_id:
                logger.error(f"无法从 URL 提取视频 ID: {url}")
                return None
            
            start_time = time.time()
            success = False
            
            try:
                # 使用代理获取字幕
                if settings.USE_PROXY:
                    proxies = await self.get_proxy()
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id, proxies=proxies)
                else:
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                if not transcript_list:
                    raise ValueError("未获取到视频字幕transcript_list")
                success = True
            finally:
                # 更新代理状态
                if settings.USE_PROXY:
                    response_time = time.time() - start_time
                    await proxy_repository.update_proxy_status(
                        proxies['http'], 
                        success=success,
                        response_time=response_time
                    )

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
                raise ValueError("未获取到视频字幕final_content")
            
            logger.info(f"成功格式化视频字幕，总行数: {len(readable_text)}")

            return final_content
            
        except Exception as e:
            logger.error(f"获取 YouTube 内容失败: {str(e)}", exc_info=True)
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
                    response = requests.get(url, proxies=proxies,verify=False)
                else:
                    response = requests.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                # 提取标题
                title = soup.find('meta', {'name': 'title'})['content']
                if not title:
                    raise ValueError("未获取到视频标题")
                success = True
            finally:
                # 更新代理状态
                if settings.USE_PROXY:
                    response_time = time.time() - start_time
                    await proxy_repository.update_proxy_status(
                        proxies['http'], 
                        success=success,
                        response_time=response_time
                    )

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
            try:
                if settings.USE_PROXY and proxies:
                    logger.info("使用代理获取作者头像")
                    yt = YouTube(url, proxies=proxies,verify=False)
                else:
                    logger.info("不使用代理获取作者头像")
                    yt = YouTube(url)
                channel = Channel(yt.channel_url)
                author_icon = channel.initial_data.get('metadata', {}).get('channelMetadataRenderer', {}).get('avatar', {}).get('thumbnails', [{}])[0].get('url', '')
                logger.info(f"获取到作者头像: {author_icon}")
            except Exception as e:
                logger.warning(f"获取作者头像失败: {str(e)}")
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
            success = False

            # 设置代理
            if settings.USE_PROXY:
                logger.info("使用代理获取章节信息")
                proxies = await self.get_proxy()
                yt = YouTube(url, proxies=proxies)
                success = True
            else:
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
        
        finally:
            # 更新代理状态
            if settings.USE_PROXY:
                await proxy_repository.update_proxy_status(
                    proxies['http'], 
                    success=success
                )