from typing import Optional, Dict
from .base import ContentFetcher, VideoInfo
from app.models.article import ArticleCreate
from app.config import settings
import assemblyai as aai
import requests
from bs4 import BeautifulSoup
import json
import re
import urllib.parse
from app.utils.logger import logger
from datetime import datetime

class ApplePodcastFetcher(ContentFetcher):
    """Apple Podcast 内容获取器"""
    
    def __init__(self):
        """初始化 AssemblyAI API"""
        aai.settings.api_key = settings.ASSEMBLYAI_API_KEY
        self.transcriber = aai.Transcriber()
        
        # 中文月份映射
        self.month_map = {
            '1月': '01', '2月': '02', '3月': '03', '4月': '04',
            '5月': '05', '6月': '06', '7月': '07', '8月': '08',
            '9月': '09', '10月': '10', '11月': '11', '12月': '12'
        }
    
    def _parse_chinese_date(self, date_str: str) -> Optional[datetime]:
        """
        将中文日期转换为datetime对象
        例如: "12月4日 2024" -> datetime(2024, 12, 4)
        """
        try:
            # 移除所有空格
            date_str = date_str.strip()
            
            # 解析年份
            year = datetime.now().year
            if date_str.endswith(str(year)):
                date_str = date_str[:-4].strip()  # 移除年份部分
            
            # 解析月份
            month = None
            for cn_month, num_month in self.month_map.items():
                if cn_month in date_str:
                    month = int(num_month)
                    date_str = date_str.replace(cn_month, '').strip()
                    break
            
            if not month:
                return None
            
            # 解析日期
            day = int(date_str.replace('��', '').strip())
            
            # 创建datetime对象
            return datetime(year, month, day)
            
        except (ValueError, AttributeError) as e:
            logger.error(f"日期解析失败: {str(e)}, 原始日期: {date_str}")
            return None
    
    async def fetch(self, url: str) -> Optional[str]:
        """
        获取 Apple Podcast 内容
        Args:
            url: Apple Podcast URL
        Returns:
            Optional[str]: 内容文本
        """
        try:
            # 1. 获取音频文件URL
            audio_url = await self._get_audio_url(url)
            if not audio_url:
                logger.error("无法获取音频URL")
                return None
                
            # 2. 使用 AssemblyAI 获取字幕
            transcript = await self._get_transcript(audio_url)
            if not transcript:
                logger.error("无法获取字幕")
                return None
                
            # 3. 格式化输出
            return self._format_transcript(transcript)
            
        except Exception as e:
            logger.error(f"获取 Apple Podcast 内容失败: {str(e)}", exc_info=True)
            return None
            
    async def _get_audio_url(self, page_url: str) -> Optional[str]:
        """获取音频文件URL"""
        try:
            session = requests.Session()
            response = session.get(page_url, verify=False, timeout=30)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            meta_element = soup.find('script', {'id': 'serialized-server-data'})
            
            if meta_element:
                data_array = json.loads(meta_element.string)
                for item in data_array:
                    if 'data' in item and 'shelves' in item['data']:
                        for shelf in item['data']['shelves']:
                            if 'items' in shelf:
                                for shelf_item in shelf['items']:
                                    if 'episodeOffer' in shelf_item:
                                        episode_data = shelf_item['episodeOffer']
                                        if 'streamUrl' in episode_data:
                                            return episode_data['streamUrl']
            return None
            
        except Exception as e:
            logger.error(f"获取音频URL失败: {str(e)}", exc_info=True)
            return None
            
    async def _get_transcript(self, audio_url: str) -> Optional[aai.Transcript]:
        """使用 AssemblyAI 获取字幕"""
        try:
            config = aai.TranscriptionConfig(
                auto_highlights=True,
                speaker_labels=True
            )
            
            transcript = self.transcriber.transcribe(
                audio_url,
                config=config
            )
            
            return transcript
            
        except Exception as e:
            logger.error(f"获取字幕失败: {str(e)}", exc_info=True)
            return None
            
    def _format_transcript(self, transcript: aai.Transcript) -> str:
        """格式化字幕输出"""
        result = []
        
        if hasattr(transcript, 'words') and transcript.words:
            current_segment = []
            segment_start = None
            SEGMENT_DURATION = 5000  # 5秒
            
            for word in transcript.words:
                if hasattr(word, 'start'):
                    if segment_start is None:
                        segment_start = word.start
                    
                    if word.start - segment_start > SEGMENT_DURATION:
                        if current_segment:
                            timestamp = self._format_timestamp(segment_start)
                            segment_text = ' '.join(current_segment)
                            result.append(f"{timestamp} {segment_text}")
                        current_segment = [word.text]
                        segment_start = word.start
                    else:
                        current_segment.append(word.text)
            
            # 添加最后一个片段
            if current_segment:
                timestamp = self._format_timestamp(segment_start)
                segment_text = ' '.join(current_segment)
                result.append(f"{timestamp} {segment_text}")
                
        return '\n'.join(result)
        
    def _format_timestamp(self, ms: int) -> str:
        """将毫秒转换为 [HH:MM:SS] 格式"""
        total_seconds = int(ms / 1000)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"[{hours:02d}:{minutes:02d}:{seconds:02d}]"
        
    def can_handle(self, url: str) -> bool:
        """
        检查是否为 Apple Podcast URL
        Args:
            url: 待检查的 URL
        Returns:
            bool: 是否可以处理
        """
        return "podcasts.apple.com" in url
        
    async def get_video_info(self, url: str) -> Optional[VideoInfo]:
        """
        获取 Podcast 基本信息
        Args:
            url: Apple Podcast URL
        Returns:
            Optional[VideoInfo]: 播客信息
        """
        try:
            logger.info(f"开始获取 Apple Podcast 信息: {url}")
            
            session = requests.Session()
            response = session.get(url, verify=False, timeout=30)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')

            logger.info(f"获取到页面内容: {soup}")
            
            # 获取标题
            title = ""
            title_element = soup.find('h1', {'class': 'headings__title', 'data-testid': 'non-editable-product-title'})
            if title_element and title_element.find('span', dir='auto'):
                title = title_element.find('span', dir='auto').text.strip()
                logger.info(f"获取到标题: {title}")
            else:
                logger.warning("未找到标题元素")
            
            # 获取播客节目名称（作者）
            author_name = ""
            podcast_link = soup.find('a', {'class': 'link-action', 'data-testid': 'click-action'})
            if podcast_link:
                author_name = podcast_link.text.strip()
                logger.info(f"获取到作者: {author_name}")
            else:
                logger.warning("未找到作者信息")
            
            # 获取发布日期并转换格式
            publish_date = None
            date_element = soup.find('li', {'class': 'svelte-16t2ez2'})
            if date_element:
                date_str = date_element.text.strip()
                # 添加年份
                current_year = datetime.now().year
                date_str = f"{date_str} {current_year}"
                # 转换为datetime对象
                publish_date = self._parse_chinese_date(date_str)
                if publish_date:
                    logger.info(f"获取到发布日期: {publish_date}")
                else:
                    logger.warning(f"日期解析失败: {date_str}")
            else:
                logger.warning("未找到发布日期元素")
            
            # 获取描述内容
            description = ""
            paragraphs_div = soup.find('div', {'data-testid': 'paragraphs'})
            if paragraphs_div:
                description = ' '.join(list(paragraphs_div.stripped_strings))
                logger.info(f"从主要元素获取到描述，长度: {len(description)}")
            
            # 如果没找到描述，尝试其他选择器
            if not description:
                logger.info("尝试使用备选方法获取描述")
                paragraphs = soup.find_all('p')
                if paragraphs:
                    description = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                    logger.info(f"从备选元素获取到描述，长度: {len(description)}")
                else:
                    logger.warning("未找到任何描述内容")
            
            # 创建 ArticleCreate 对象
            article = ArticleCreate(
                title=title,
                content=description,
                channel="Apple Podcast",
                tags=["播客"],
                original_link=url,
                publish_date=publish_date
            )
            logger.info("成功创建 ArticleCreate 对象")
            
            # 创建作者信息
            author = {
                "name": author_name,
                "platform": "Apple Podcast"
            }
            
            # 创建并返回 VideoInfo 对象
            return VideoInfo(
                title=title,
                description=description,
                author=author,
                article=article
            )
            
        except Exception as e:
            logger.error(f"获取播客信息失败: {str(e)}", exc_info=True)
            return None

    async def get_chapters(self, url: str) -> Optional[str]:
        """
        获取播客章节信息
        Args:
            url: Apple Podcast URL
        Returns:
            Optional[str]: 章节信息
        """
        # TODO: 实现获取章节信息的逻辑
        pass 