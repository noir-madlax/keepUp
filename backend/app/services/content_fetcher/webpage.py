from typing import Optional
from .base import ContentFetcher, VideoInfo
from app.utils.logger import logger
from app.models.article import ArticleCreate
from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime
from urllib.parse import urlparse, urljoin
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3

# 禁用不安全请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WebPageFetcher(ContentFetcher):
    """通用网页内容获取器"""
    
    def __init__(self):
        self.session = self.create_session()
        
    def create_session(self):
        """创建一个带有重试机制的会话"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def can_handle(self, url: str) -> bool:
        """检查是否是普通网页URL"""
        known_platforms = [
            'youtube.com', 'youtu.be',
            'podcasts.apple.com', 
            'open.spotify.com',
            'xiaoyuzhoufm.com'
        ]
        return not any(platform in url for platform in known_platforms)
    
    def clean_text(self, text):
        """改进的文本清理方法"""
        if not text:
            return ""
        
        # 基本清理
        text = text.strip()
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除特殊字符
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        
        # 移除重复的标点符号
        text = re.sub(r'([。！？，、；：""''）》】\.!?,;:\)\}])\1+', r'\1', text)
        
        # 修复常见的排版问题
        text = re.sub(r'([。！？\.!?])([^"\'"\]\)\}）》】])', r'\1 \2', text)
        
        return text
    
    def is_valid_content(self, element):
        """改进的内容验证方法"""
        if not element:
            return False
        
        # 检查元素的可见性
        style = element.get('style', '').lower()
        if 'display: none' in style or 'visibility: hidden' in style:
            return False
        
        # 排除无效内容
        invalid_patterns = [
            'nav', 'footer', 'header', 'menu', 'sidebar', 'ad', 
            'comment', 'social', 'related', 'share', 'cookie',
            'popup', 'banner', 'copyright', 'tracking', 'search',
            'newsletter', 'subscribe'
        ]
        
        # 检查元素的class和id
        for attr in ['class', 'id']:
            if element.get(attr):
                attr_value = ' '.join(element[attr] if isinstance(element[attr], list) else [element[attr]])
                attr_value = attr_value.lower()
                if any(pattern in attr_value for pattern in invalid_patterns):
                    return False
        
        # 检查是否包含有效的文本内容
        text = element.get_text(strip=True)
        if not text or len(text) < 20:
            return False
        
        return True
    
    def calculate_text_density(self, element):
        """计算元素的文本密度"""
        text_length = len(element.get_text(strip=True))
        html_length = len(str(element))
        if html_length == 0:
            return 0
        return text_length / html_length
    
    def extract_main_content(self, soup):
        """提取主要内容"""
        main_content = []
        
        # 1. 首先尝试找到最密集的文本区域
        text_blocks = []
        for element in soup.find_all(['div', 'article', 'section', 'main']):
            if not self.is_valid_content(element):
                continue
            
            density = self.calculate_text_density(element)
            text_length = len(element.get_text(strip=True))
            
            if text_length > 100:
                text_blocks.append({
                    'element': element,
                    'density': density,
                    'length': text_length
                })
        
        # 按文本密度和长度排序
        text_blocks.sort(key=lambda x: (x['density'], x['length']), reverse=True)
        
        # 2. 如果找到了高密度区域
        if text_blocks:
            main_element = text_blocks[0]['element']
            
            # 提取段落和标题
            for element in main_element.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                text = self.clean_text(element.get_text())
                if text and len(text) > 20:
                    if element.name.startswith('h'):
                        main_content.append(f"\n### {text}\n")
                    else:
                        main_content.append(text)
        
        # 3. 如果上述方法没有提取到足够的内容，使用备选方案
        if len(main_content) < 3:
            logger.info("使用备选方案提取内容...")
            paragraphs = soup.find_all('p')
            
            valid_paragraphs = []
            for p in paragraphs:
                text = self.clean_text(p.get_text())
                if len(text) > 50:
                    valid_paragraphs.append((text, len(text)))
            
            valid_paragraphs.sort(key=lambda x: x[1], reverse=True)
            
            for text, _ in valid_paragraphs[:10]:
                if text not in main_content:
                    main_content.append(text)
        
        return "\n\n".join(main_content)
    
    async def fetch(self, url: str) -> Optional[str]:
        """获取网页内容"""
        try:
            response = self.session.get(url, verify=False, timeout=30)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 移除script和style标签
            for script in soup(['script', 'style']):
                script.decompose()
            
            # 提取主要内容
            content = self.extract_main_content(soup)
            
            return content
            
        except Exception as e:
            logger.error(f"获取网页内容失败: {str(e)}")
            return None
    
    async def get_video_info(self, url: str) -> Optional[VideoInfo]:
        """获取网页信息"""
        try:
            response = self.session.get(url, verify=False, timeout=30)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 获取标题
            title = soup.title.string if soup.title else url
            title = self.clean_text(title)
            
            # 获取描述
            description = ""
            meta_desc = soup.find('meta', {'name': 'description'})
            if meta_desc:
                description = self.clean_text(meta_desc.get('content', ''))
            
            if not description:
                # 如果没有meta描述,使用正文前200个字符作为描述
                content = self.extract_main_content(soup)
                description = content[:200] + "..." if content else ""
            
            # 获取作者信息
            author_name = "Unknown"
            author_meta = soup.find('meta', {'name': ['author', 'Article:author']})
            if author_meta:
                author_name = self.clean_text(author_meta.get('content', 'Unknown'))
            
            # 获取发布日期
            publish_date = datetime.now()
            date_meta = soup.find('meta', {'property': 'article:published_time'})
            if date_meta:
                try:
                    publish_date = datetime.fromisoformat(date_meta.get('content', '').split('T')[0])
                except:
                    pass
            
            # 获取封面图片
            cover_image_url = None
            og_image = soup.find('meta', {'property': 'og:image'})
            if og_image:
                cover_image_url = og_image.get('content')
                if cover_image_url and not cover_image_url.startswith(('http://', 'https://')):
                    cover_image_url = urljoin(url, cover_image_url)
            
            # 创建文章对象
            article = ArticleCreate(
                title=title,
                content=description,
                channel="webpage",
                tags=["webpage"],
                original_link=url,
                publish_date=publish_date,
                cover_image_url=cover_image_url
            )
            
            # 创建作者信息
            author = {
                "name": author_name,
                "platform": "webpage",
                "icon": None
            }
            
            return VideoInfo(
                title=title,
                description=description,
                author=author,
                article=article
            )
            
        except Exception as e:
            logger.error(f"获取网页信息失败: {str(e)}")
            return None
    
    async def get_chapters(self, url: str) -> Optional[str]:
        """获取网页章节信息"""
        try:
            response = self.session.get(url, verify=False, timeout=30)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 获取所有标题标签
            headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            
            if not headers:
                return None
            
            # 构建章节信息
            chapters = []
            for header in headers:
                text = self.clean_text(header.get_text())
                if text:
                    chapters.append(f"{header.name}: {text}")
            
            return "\n".join(chapters)
            
        except Exception as e:
            logger.error(f"获取网页章节信息失败: {str(e)}")
            return None 