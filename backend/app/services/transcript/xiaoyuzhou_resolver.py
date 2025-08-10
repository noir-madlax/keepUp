import re
import time
from difflib import SequenceMatcher
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from app.utils.logger import logger


class XiaoYuZhouResolver:
    """Resolve XiaoYuZhou episode audio URL by matching episode title.

    This module avoids downloading audio; it only finds the best-matching
    episode and returns its direct audio URL from the <meta property="og:audio"> tag.
    """

    BASE_URL = "https://www.xiaoyuzhoufm.com"

    def __init__(self, user_agent: Optional[str] = None):
        self.headers = {
            "User-Agent": user_agent
            or (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
            )
        }

    @staticmethod
    def _normalize_title(text: str) -> str:
        text = text or ""
        text = re.sub(r"\s+", "", text)
        text = re.sub(r"[\[\]（）()【】<>《》:：,.!?！？、·-]", "", text)
        return text.lower()

    def _find_episode_links(self, podcast_url: str) -> list[str]:
        logger.info(f"[XZ Resolver] Fetch podcast page: {podcast_url}")
        resp = requests.get(podcast_url, headers=self.headers, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        links: list[str] = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if isinstance(href, str) and href.startswith("/episode/"):
                links.append(urljoin(self.BASE_URL, href))
        # de-dup while preserving order
        uniq = list(dict.fromkeys(links))
        logger.info(f"[XZ Resolver] episode links found: {len(uniq)}")
        return uniq

    def _get_episode_meta(self, episode_url: str) -> tuple[str, str]:
        resp = requests.get(episode_url, headers=self.headers, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        title_meta = soup.find("meta", property="og:title")
        audio_meta = soup.find("meta", property="og:audio")
        title = title_meta.get("content", "") if title_meta else ""
        audio = audio_meta.get("content", "") if audio_meta else ""
        return title, audio

    def find_episode_audio(self, podcast_url: str, title: str, threshold: float = 0.75) -> Optional[str]:
        """Find best-matching episode by title and return audio URL.

        Args:
            podcast_url: XiaoYuZhou podcast page URL
            title: Title to match (from YouTube)
            threshold: Similarity threshold [0,1]
        Returns:
            Direct audio URL if found, else None
        """
        target = self._normalize_title(title)
        if not target:
            return None

        best_audio: Optional[str] = None
        best_score: float = 0.0

        for ep in self._find_episode_links(podcast_url):
            try:
                ep_title, ep_audio = self._get_episode_meta(ep)
                if not ep_title or not ep_audio:
                    continue
                score = SequenceMatcher(None, target, self._normalize_title(ep_title)).ratio()
                logger.info(f"[XZ Resolver] candidate score={score:.3f} title='{ep_title[:60]}' audio={'yes' if ep_audio else 'no'}")
                if score > best_score:
                    best_score = score
                    best_audio = ep_audio
                if best_score >= 0.99:  # perfect early-stop
                    break
            except Exception:
                continue
        ok = best_audio if best_score >= threshold else None
        logger.info(f"[XZ Resolver] best_score={best_score:.3f} threshold={threshold} matched={'yes' if ok else 'no'}")
        return ok


