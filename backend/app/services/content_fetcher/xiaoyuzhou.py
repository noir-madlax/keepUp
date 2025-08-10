from typing import Optional, Dict
from .base import ContentFetcher, VideoInfo, AuthorInfo
import re
from app.utils.logger import logger
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from datetime import datetime
from app.models.article import ArticleCreate
from app.services.transcript.tencent_asr import TencentASRClient
from app.config import settings

class XiaoYuZhouFetcher(ContentFetcher):
    """Fetcher for XiaoYuZhou pages with optional proxy and retry session"""

    def __init__(self) -> None:
        # Build a resilient session with retries and headers
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            connect=3,
            read=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set a realistic browser User-Agent and language headers
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            ),
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        })

        # Optional proxy support via settings
        if getattr(settings, "USE_PROXY", False) and getattr(settings, "PROXY_URL", None):
            proxy_url = settings.PROXY_URL
            self.session.proxies = {"http": proxy_url, "https": proxy_url}
            masked = re.sub(r":[^@]+@", ":***@", proxy_url)
            logger.info(f"[XiaoYuZhou] Using proxy for requests: {masked}")

    def _get_soup(self, url: str) -> BeautifulSoup:
        """Request a URL and return BeautifulSoup, with logging on failures."""
        logger.info(f"[XiaoYuZhou][Step] HTTP request start: {url}")
        try:
            resp = self.session.get(url, timeout=20)
            # Log basic diagnostics before raising
            logger.info(
                f"[XiaoYuZhou][Step] HTTP response: status={resp.status_code}, len={len(resp.text)}"
            )
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "html.parser")
        except Exception as e:
            logger.error(f"[XiaoYuZhou][Step] HTTP request failed: {type(e).__name__}: {e}")
            raise
    def can_handle(self, url: str) -> bool:
        """检查是否是小宇宙 URL"""
        return 'xiaoyuzhoufm.com' in url
    
    async def fetch(self, url: str) -> Optional[str]:
        """获取小宇宙内容"""
        try:
            logger.info(f"[XiaoYuZhou][Step] start fetch: {url}")
            # 解析音频直链
            soup = self._get_soup(url)
            audio_meta = soup.find('meta', property='og:audio')
            audio_url = audio_meta.get('content', '') if audio_meta else ''
            if not audio_url:
                logger.warning(f"[XiaoYuZhou][Step] og:audio missing")
            else:
                logger.info(f"[XiaoYuZhou][Step] audio_url parsed")

            # 基础信息（用于 content 头部）
            vinfo = await self.get_video_info(url)

            transcript_text = None
            if audio_url:
                try:
                    asr = TencentASRClient()
                    task_id = asr.create_task(audio_url)
                    logger.info(f"[XiaoYuZhou] Tencent ASR create task_id={task_id}")
                    result = asr.poll_result(task_id)
                    status = (result.get('Data') or {}).get('StatusStr')
                    logger.info(f"[XiaoYuZhou] Tencent ASR poll status={status}")
                    transcript_text = asr.to_bracketed_transcript(result)
                    if transcript_text:
                        logger.info(f"[XiaoYuZhou] Tencent ASR success length={len(transcript_text)}")
                except Exception as e:
                    logger.warning(f"[XiaoYuZhou] Tencent ASR failed: {e}")

            parts = []
            if vinfo:
                parts.append(f"标题: {vinfo.title}")
                parts.append(f"作者: {vinfo.author}")
                parts.append(f"描述: {vinfo.description}")
            if transcript_text:
                parts.append(f"转录内容: {transcript_text}")

            content = "\n\n".join(parts) if parts else None
            return content
        except Exception as e:
            logger.error(f"[XiaoYuZhou] fetch failed: {e}")
            return None

    async def get_video_info(self, url: str) -> Optional[VideoInfo]:
        """获取小宇宙信息"""
        try:
            logger.info(f"[XiaoYuZhou][Step] start get_video_info: {url}")
            soup = self._get_soup(url)

            title = ''
            desc = ''
            cover = ''
            podcast_title = ''
            podcast_icon = ''
            publish_date = None

            title_meta = soup.find('meta', property='og:title')
            if title_meta:
                title = title_meta.get('content', '').strip()
                logger.info(f"[XiaoYuZhou][Step] title extracted: {bool(title)}")
            else:
                logger.warning("[XiaoYuZhou][Step] og:title missing")
            image_meta = soup.find('meta', property='og:image')
            if image_meta:
                cover = image_meta.get('content', '').strip()
                logger.info(f"[XiaoYuZhou][Step] cover extracted: {bool(cover)}")
            else:
                logger.warning("[XiaoYuZhou][Step] og:image missing")

            header = soup.find(lambda tag: tag.name == 'header' and tag.find('h1'))
            if header:
                logger.info("[XiaoYuZhou][Step] header found")
                a = header.find('a', href=re.compile(r'^/podcast/'))
                if a:
                    podcast_title = a.get_text(strip=True)
                    logger.info("[XiaoYuZhou][Step] podcast title extracted")
                # side-avatar 作为播客图标
                for img in header.find_all('img'):
                    cls = ' '.join(img.get('class', []))
                    src = img.get('src', '')
                    if 'side-avatar' in cls and src:
                        podcast_icon = src.split('@small')[0]
                        break
                # 发表时间
                t = header.find('time')
                if t and t.has_attr('datetime'):
                    try:
                        publish_date = datetime.fromisoformat(t['datetime'].replace('Z', '+00:00'))
                        logger.info("[XiaoYuZhou][Step] publish date parsed")
                    except Exception:
                        publish_date = None
                        logger.warning("[XiaoYuZhou][Step] publish date parse failed")
            else:
                logger.warning("[XiaoYuZhou][Step] header section missing")

            author = {
                'name': podcast_title or '未知作者',
                'icon': podcast_icon,
            }

            article = ArticleCreate(
                title=title or '未知标题',
                content='',
                channel='XiaoYuZhou',
                tags=['播客', '小宇宙'],
                original_link=url,
                publish_date=publish_date,
                cover_image_url=cover
            )

            logger.info(f"[XiaoYuZhou][Step] parsed fields OK")

            return VideoInfo(
                title=title or '未知标题',
                description=desc,
                author=author,
                article=article
            )
        except Exception as e:
            logger.error(f"[XiaoYuZhou][Step] get_video_info failed: {type(e).__name__}: {e}")
            return None

    async def get_chapters(self, url: str) -> Optional[str]:
        """获取小宇宙章节信息"""
        logger.info(f"[XiaoYuZhou][Step] chapters not supported")
        return None

    async def get_author_info(self, url: str) -> Optional[AuthorInfo]:
        """获取小宇宙播客作者信息"""
        try:
            soup = self._get_soup(url)
            header = soup.find(lambda tag: tag.name == 'header' and tag.find('h1'))
            name = None
            icon = None
            if header:
                a = header.find('a', href=re.compile(r'^/podcast/'))
                if a:
                    name = a.get_text(strip=True)
                for img in header.find_all('img'):
                    cls = ' '.join(img.get('class', []))
                    src = img.get('src', '')
                    if 'side-avatar' in cls and src:
                        icon = src.split('@small')[0]
                        break
            if name:
                return AuthorInfo(name=name, icon=icon or '', platform='XiaoYuZhou')
            return None
        except Exception:
            return None