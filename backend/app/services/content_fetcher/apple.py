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
from datetime import datetime, timedelta

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
        解析多种格式的日期字符串为datetime对象
        支持的格式:
        - 中文格式: "12月4日 2024"
        - 英文相对格��: "1 DAY AGO 2024", "2 DAYS AGO 2024"
        - 英文日期格式: "DEC 4 2024", "DECEMBER 4 2024"
        """
        try:
            # 移除所有多余的空格并转换为大写以统一处理
            date_str = ' '.join(date_str.strip().split()).upper()
            
            # 处理相对日期格式 (例如: "1 DAY AGO 2024")
            if "AGO" in date_str:
                days_ago_match = re.match(r'(\d+)\s+DAY[S]?\s+AGO\s+(\d{4})', date_str)
                if days_ago_match:
                    days = int(days_ago_match.group(1))
                    year = int(days_ago_match.group(2))
                    return datetime.now().replace(year=year) - timedelta(days=days)
            
            # 处理英文月份格式
            english_months = {
                'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
                'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12,
                'JANUARY': 1, 'FEBRUARY': 2, 'MARCH': 3, 'APRIL': 4, 'JUNE': 6,
                'JULY': 7, 'AUGUST': 8, 'SEPTEMBER': 9, 'OCTOBER': 10,
                'NOVEMBER': 11, 'DECEMBER': 12
            }
            
            for month_name, month_num in english_months.items():
                if month_name in date_str:
                    # 匹配 "DEC 4 2024" 或 "DECEMBER 4 2024" 格式
                    match = re.search(fr'{month_name}\s+(\d+)\s+(\d{{4}})', date_str)
                    if match:
                        day = int(match.group(1))
                        year = int(match.group(2))
                        return datetime(year, month_num, day)
            
            # 处理中文格式
            year = datetime.now().year
            if date_str.endswith(str(year)):
                date_str = date_str[:-4].strip()
            
            # 解析中文月份
            month = None
            for cn_month, num_month in self.month_map.items():
                if cn_month in date_str:
                    month = int(num_month)
                    date_str = date_str.replace(cn_month, '').strip()
                    break
            
            if month:
                # 解析日期
                day = int(date_str.replace('日', '').strip())
                return datetime(year, month, day)
            
            return None
            
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
            
            # 取标题
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
            
            # 获取缩略图URL
            thumbnail_url = self._get_thumbnail_url(soup)
            
            # 创建 ArticleCreate 对象
            article = ArticleCreate(
                title=title,
                content=description,
                channel="Apple Podcast",
                tags=["播客"],
                original_link=url,
                publish_date=publish_date,
                cover_image_url=thumbnail_url  # 使用 cover_image_url 而不是 thumbnail
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

    def _get_thumbnail_url(self, soup: BeautifulSoup) -> Optional[str]:
        """
        从页面解析获取播客缩略图URL
        Args:
            soup: BeautifulSoup对象
        Returns:
            Optional[str]: 缩略图URL
        """
        try:
            thumbnail_url = None
            picture_element = soup.find('picture', {'class': 'svelte-3e3mdo'})
            
            if picture_element:
                # 尝试获取最高质量的图片URL
                source_elements = picture_element.find_all('source')
                if source_elements:
                    # 从srcset属性中提取最后一个URL（通常是最高质量的）
                    for source in source_elements:
                        srcset = source.get('srcset', '')
                        if srcset:
                            # 分割srcset并获取最后一个URL
                            urls = [url.strip().split(' ')[0] for url in srcset.split(',')]
                            if urls:
                                thumbnail_url = urls[-1]
                                break
                
                # 如果source标签中没找到，尝试从img标签获取
                if not thumbnail_url:
                    img_element = picture_element.find('img')
                    if img_element:
                        thumbnail_url = img_element.get('src')
            
            logger.info(f"获取到缩略图URL: {thumbnail_url}")
            return thumbnail_url
            
        except Exception as e:
            logger.error(f"获取缩略图URL失败: {str(e)}")
            return None