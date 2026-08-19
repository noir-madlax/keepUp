"""Pure transcript text helpers — no cloud SDK imports."""
from __future__ import annotations

import re
from typing import Optional

INNER_TIMESTAMP_RE = re.compile(r"\[\d+:\d+(?:\.\d+)?,\d+:\d+(?:\.\d+)?\]\s*")


def ms_to_hhmmss(ms: float) -> str:
    """Convert millisecond offsets from Supadata chunks to [HH:MM:SS] prefixes."""
    seconds = max(0, int(float(ms) / 1000.0))
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def strip_inner_timestamps(text: Optional[str]) -> str:
    if not text:
        return ""
    return INNER_TIMESTAMP_RE.sub("", text).strip()


def build_youtube_content(
    title: str,
    author,
    description: Optional[str],
    transcript: Optional[str],
) -> Optional[str]:
    """Assemble LLM input. Returns None when there is no real transcript."""
    if not transcript or not str(transcript).strip():
        return None
    return "\n\n".join(
        [
            f"标题: {title}",
            f"作者: {author}",
            f"描述: {description or ''}",
            f"转录内容: {str(transcript).strip()}",
        ]
    )
