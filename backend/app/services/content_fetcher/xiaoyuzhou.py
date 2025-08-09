from typing import Optional, Dict
from .base import ContentFetcher, VideoInfo, AuthorInfo
import re
from app.utils.logger import logger
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from app.models.article import ArticleCreate
from app.services.transcript.tencent_asr import TencentASRClient

class XiaoYuZhouFetcher(ContentFetcher):
    def can_handle(self, url: str) -> bool:
        """检查是否是小宇宙 URL"""
        return 'xiaoyuzhoufm.com' in url
    
    async def fetch(self, url: str) -> Optional[str]:
        """获取小宇宙内容"""
        try:
            logger.info(f"[XiaoYuZhou] start fetch: {url}")
            # 解析音频直链
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            audio_meta = soup.find('meta', property='og:audio')
            audio_url = audio_meta.get('content', '') if audio_meta else ''
            if not audio_url:
                logger.warning(f"[XiaoYuZhou] og:audio missing")
            else:
                logger.info(f"[XiaoYuZhou] audio_url: {audio_url}")

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
            logger.info(f"[XiaoYuZhou] start get_video_info: {url}")
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')

            title = ''
            desc = ''
            cover = ''
            podcast_title = ''
            podcast_icon = ''
            publish_date = None

            title_meta = soup.find('meta', property='og:title')
            if title_meta:
                title = title_meta.get('content', '').strip()
            image_meta = soup.find('meta', property='og:image')
            if image_meta:
                cover = image_meta.get('content', '').strip()

            header = soup.find(lambda tag: tag.name == 'header' and tag.find('h1'))
            if header:
                a = header.find('a', href=re.compile(r'^/podcast/'))
                if a:
                    podcast_title = a.get_text(strip=True)
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
                    except Exception:
                        publish_date = None

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

            logger.info(f"[XiaoYuZhou] parsed fields title='{title}', author='{podcast_title}', cover='{cover}'")

            return VideoInfo(
                title=title or '未知标题',
                description=desc,
                author=author,
                article=article
            )
        except Exception as e:
            logger.error(f"[XiaoYuZhou] get_video_info failed: {e}")
            return None

    async def get_chapters(self, url: str) -> Optional[str]:
        """获取小宇宙章节信息"""
        logger.info(f"[XiaoYuZhou] chapters not supported")
        return None

    async def get_author_info(self, url: str) -> Optional[AuthorInfo]:
        """获取小宇宙播客作者信息"""
        try:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
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