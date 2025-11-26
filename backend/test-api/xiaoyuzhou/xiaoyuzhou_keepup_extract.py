import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.xiaoyuzhoufm.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
    )
}


def _text(el: Optional[object]) -> str:
    return (el.get_text(strip=True) if el else "").strip()


def _clean_img_url(src: str) -> str:
    # Remove @small suffix if present
    if not src:
        return src
    return src.split("@small")[0]


def _parse_minutes_to_seconds(text: str) -> Optional[int]:
    # Match like "122分钟" or "79分钟"
    m = re.search(r"(\d+)\s*分钟", text)
    if m:
        return int(m.group(1)) * 60
    return None


@dataclass
class Author:
    name: Optional[str] = None
    icon: Optional[str] = None


@dataclass
class EpisodeExtract:
    title: str
    audio_url: str
    channel: str = "XiaoYuZhou"
    original_link: Optional[str] = None
    author: Author = field(default_factory=Author)
    cover_image_url: Optional[str] = None
    podcast_title: Optional[str] = None
    podcast_link: Optional[str] = None
    publish_date: Optional[str] = None  # ISO 8601
    duration_seconds: Optional[int] = None
    plays: Optional[int] = None
    comments: Optional[int] = None
    description: Optional[str] = None


def extract_episode_fields(url: str) -> EpisodeExtract:
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Required fields
    title_meta = soup.find("meta", property="og:title")
    if not title_meta:
        raise RuntimeError("Missing og:title")
    title = title_meta.get("content", "").strip()

    audio_meta = soup.find("meta", property="og:audio")
    if not audio_meta:
        raise RuntimeError("Missing og:audio")
    audio_url = audio_meta.get("content", "").strip()

    # Optional fields (best-effort)
    cover_meta = soup.find("meta", property="og:image")
    cover_image = cover_meta.get("content", "").strip() if cover_meta else None

    # Header block parsing (robust to class hash changes)
    header = soup.find(lambda tag: tag.name == "header" and tag.find("h1"))
    podcast_title = None
    podcast_link = None
    author_icon = None
    if header:
        h1 = header.find("h1")
        # Title may include decorations; prefer og:title already used
        # Podcast title and link
        podcast_a = header.find("a", href=re.compile(r"^/podcast/"))
        if podcast_a:
            podcast_title = _text(podcast_a)
            podcast_link = urljoin(BASE_URL, podcast_a.get("href", ""))

        # Avatars: main avatar is episode cover; side-avatar is podcast icon
        # Find img elements in avatar container
        imgs = header.find_all("img")
        for img in imgs:
            cls = " ".join(img.get("class", []))
            src = _clean_img_url(img.get("src", ""))
            alt = img.get("alt", "")
            if "avatar" in cls and not cover_image:
                cover_image = src or cover_image
            if "side-avatar" in cls and not author_icon:
                author_icon = src

        # Info line: duration, datetime, stats
        info = header.find(lambda t: t.name == "div" and "info" in " ".join(t.get("class", [])))
        if info:
            # duration
            duration_seconds = _parse_minutes_to_seconds(info.get_text(" ", strip=True))
        else:
            duration_seconds = None

        # datetime
        time_tag = header.find("time")
        publish_date = time_tag.get("datetime") if time_tag and time_tag.has_attr("datetime") else None

        # stats
        plays = None
        comments = None
        for stat in header.find_all("div", class_=re.compile(r"stat")):
            text = _text(stat)
            if text.isdigit():
                # Heuristic: first stat is plays, second is comments
                if plays is None:
                    plays = int(text)
                elif comments is None:
                    comments = int(text)
        # Fallback: scan icons alt
        if plays is None:
            icon_play = header.find("img", alt=re.compile("播放数"))
            if icon_play and icon_play.parent:
                try:
                    plays = int(icon_play.parent.get_text(strip=True))
                except Exception:
                    plays = None
        if comments is None:
            icon_cmt = header.find("img", alt=re.compile("评论数"))
            if icon_cmt and icon_cmt.parent:
                try:
                    comments = int(icon_cmt.parent.get_text(strip=True))
                except Exception:
                    comments = None
    else:
        duration_seconds = None
        publish_date = None
        plays = None
        comments = None

    # Description / show notes (best-effort)
    # Try common containers
    description = None
    candidates = soup.find_all(["article", "section", "div"], string=False)
    for c in candidates:
        text = c.get_text("\n", strip=True)
        # Heuristic: long-ish text with line breaks and not containing too many UI labels
        if text and len(text) >= 120 and ("评论" not in text or len(text) > 400):
            description = text
            break

    author_name = podcast_title  # Treat podcast as author/channel for KeepUp

    result = EpisodeExtract(
        title=title,
        audio_url=audio_url,
        channel="XiaoYuZhou",
        original_link=url,
        author=Author(name=author_name, icon=author_icon),
        cover_image_url=cover_image,
        podcast_title=podcast_title,
        podcast_link=podcast_link,
        publish_date=publish_date,
        duration_seconds=duration_seconds,
        plays=plays,
        comments=comments,
        description=description,
    )
    return result


if __name__ == "__main__":
    import sys

    urls = sys.argv[1:] or [
        "https://www.xiaoyuzhoufm.com/episode/66aa57e233ddcbb53c740c53",
        "https://www.xiaoyuzhoufm.com/episode/6638509903bcdd73a9b4ca21",
    ]

    out = []
    for u in urls:
        try:
            data = extract_episode_fields(u)
            out.append(asdict(data))
        except Exception as e:
            out.append({"url": u, "error": str(e)})

    print(json.dumps(out, ensure_ascii=False, indent=2))


