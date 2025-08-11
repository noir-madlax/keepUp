from typing import Optional, Dict
from .base import ContentFetcher, VideoInfo, AuthorInfo
import re
from app.utils.logger import logger
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from app.models.article import ArticleCreate
from app.services.transcript.tencent_asr import TencentASRClient
from app.config import settings
from app.services.transcript.xiaoyuzhou_resolver import XiaoYuZhouResolver

class XiaoYuZhouFetcher(ContentFetcher):
    """Fetcher for XiaoYuZhou pages with anti-bot aware access and verbose logging"""

    def __init__(self) -> None:
        # Use the exact headers/methodology as XiaoYuZhouResolver to avoid wind-control
        self.resolver = XiaoYuZhouResolver()
        self.default_headers = dict(self.resolver.headers)
        # Align language hints
        self.default_headers.setdefault("Accept-Language", "zh-CN,zh;q=0.9,en;q=0.8")

        # Do NOT use proxy for XiaoYuZhou even if configured globally
        if getattr(settings, "USE_PROXY", False) and getattr(settings, "PROXY_URL", None):
            logger.info("[XiaoYuZhou] Proxy detected in settings but ignored for XiaoYuZhou fetcher")

    def _get_soup(self, url: str) -> BeautifulSoup:
        """Request a URL and return BeautifulSoup, with logging on failures."""
        logger.info(f"[XiaoYuZhou][Step] HTTP request start: {url}")
        try:
            resp = requests.get(url, headers=self.default_headers, timeout=20)
            # Log basic diagnostics before raising
            logger.info(
                f"[XiaoYuZhou][Step] HTTP response: status={resp.status_code}, len={len(resp.text)}"
            )
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "html.parser")
        except Exception as e:
            logger.error(f"[XiaoYuZhou][Step] HTTP request failed: {type(e).__name__}: {e}")
            raise

    def _extract_episode_id(self, url: str) -> str:
        m = re.search(r"/episode/([A-Za-z0-9]+)", url)
        return m.group(1) if m else ""

    def _extract_podcast_url(self, soup: BeautifulSoup) -> Optional[str]:
        try:
            header = soup.find(lambda tag: tag.name == 'header' and tag.find('h1'))
            if not header:
                return None
            a = header.find('a', href=re.compile(r'^/podcast/'))
            if a and a.has_attr('href'):
                return f"https://www.xiaoyuzhoufm.com{a['href']}"
            return None
        except Exception:
            return None

    def _normalize_icon_url(self, src: str) -> str:
        """Ensure the podcast/author icon URL is absolute and usable by clients.
        - Handles protocol-relative URLs (//)
        - Handles site-relative URLs (/...)
        - Trims known size suffix like '@small'
        """
        if not src:
            return ''
        # Trim size suffix if present
        if '@small' in src:
            src = src.split('@small')[0]
        # Protocol-relative
        if src.startswith('//'):
            return f"https:{src}"
        # Site-relative
        if src.startswith('/'):
            return f"https://www.xiaoyuzhoufm.com{src}"
        return src

    def _fallback_audio_via_podcast(self, episode_url: str, episode_id: str, podcast_url: str) -> Optional[str]:
        try:
            logger.info(f"[XiaoYuZhou][Step] Fallback via podcast page: {podcast_url}")
            ep_links = self.resolver._find_episode_links(podcast_url)
            logger.info(f"[XiaoYuZhou][Step] Podcast episodes discovered: {len(ep_links)}")
            # Match by episode id
            target = None
            for link in ep_links:
                if episode_id and episode_id in link:
                    target = link
                    break
            if not target:
                logger.warning(f"[XiaoYuZhou][Step] Fallback match by id failed: id='{episode_id}'")
                return None
            logger.info(f"[XiaoYuZhou][Step] Fallback target episode: {target}")
            # Reuse resolver path to read meta
            title, audio = self.resolver._get_episode_meta(target)
            logger.info(f"[XiaoYuZhou][Step] Fallback meta extracted: title={'yes' if title else 'no'}, audio={'yes' if audio else 'no'}")
            return audio or None
        except Exception as e:
            logger.error(f"[XiaoYuZhou][Step] Fallback via podcast failed: {type(e).__name__}: {e}")
            return None
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
                # Try fallback via podcast list if possible
                podcast_url = self._extract_podcast_url(soup)
                if podcast_url:
                    episode_id = self._extract_episode_id(url)
                    logger.info(f"[XiaoYuZhou][Step] Attempt fallback using podcast_url and episode_id: {podcast_url} | {episode_id}")
                    audio_url = self._fallback_audio_via_podcast(url, episode_id, podcast_url) or ''
                    if audio_url:
                        logger.info(f"[XiaoYuZhou][Step] Fallback audio_url parsed")
                    else:
                        logger.warning(f"[XiaoYuZhou][Step] Fallback audio_url not found")
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
                        podcast_icon = self._normalize_icon_url(src)
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
                        icon = self._normalize_icon_url(src)
                        break
            if name:
                return AuthorInfo(name=name, icon=icon or '', platform='XiaoYuZhou')
            return None
        except Exception:
            return None