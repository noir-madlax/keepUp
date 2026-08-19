"""Supadata transcript client.

Native captions stay on the existing `/v1/youtube/transcript` path.
When those are missing, this client calls `/v1/transcript?mode=auto` so
Supadata can fall back to Whisper on their side — Lightsail never downloads
YouTube audio.
"""
from __future__ import annotations

import os
import time
from typing import Any, Optional

import requests

try:
    from dotenv import load_dotenv
except ImportError:  # tests / slim environments
    def load_dotenv(*_args, **_kwargs):
        return False

from app.services.transcript.text_utils import ms_to_hhmmss

try:
    from app.utils.logger import logger
except Exception:  # pragma: no cover
    import logging

    logger = logging.getLogger(__name__)


class SupadataTranscriptClient:
    """GET /v1/transcript with job polling for long Whisper jobs."""

    BASE_URL = "https://api.supadata.ai/v1"

    def __init__(self) -> None:
        load_dotenv()
        self.api_key = os.getenv("SUPERDATA_KEY") or os.getenv("superdata_KEY")
        self.poll_interval = int(os.getenv("SUPADATA_POLL_INTERVAL", "2"))
        self.poll_timeout = int(os.getenv("SUPADATA_POLL_TIMEOUT", "1800"))
        self.request_timeout = int(os.getenv("SUPADATA_GENERATE_TIMEOUT", "150"))

    def _headers(self) -> dict[str, str]:
        return {"x-api-key": self.api_key or ""}

    @staticmethod
    def to_bracketed_transcript(content: Any) -> str:
        if isinstance(content, str):
            text = content.strip()
            return f"[00:00:00] {text}" if text else ""
        if not isinstance(content, list):
            return ""
        lines: list[str] = []
        for item in content:
            if not isinstance(item, dict):
                continue
            text = strip_text(item.get("text"))
            if not text:
                continue
            ts = ms_to_hhmmss(item.get("offset") or 0)
            lines.append(f"[{ts}] {text}")
        return "\n".join(lines)

    def transcribe(self, video_url: str, mode: str = "auto") -> Optional[str]:
        if not self.api_key:
            logger.warning("[YT Supadata] SUPERDATA_KEY missing; skip Whisper fallback")
            return None
        if not video_url:
            return None

        logger.info(f"[YT Supadata] mode={mode} url={video_url}")
        response = requests.get(
            f"{self.BASE_URL}/transcript",
            headers=self._headers(),
            params={"url": video_url, "mode": mode, "text": "false"},
            timeout=self.request_timeout,
        )
        if response.status_code == 202:
            job_id = (response.json() or {}).get("jobId")
            if not job_id:
                logger.warning("[YT Supadata] 202 without jobId")
                return None
            logger.info(f"[YT Supadata] async job_id={job_id}")
            return self._poll_job(job_id)
        if response.status_code != 200:
            logger.warning(
                f"[YT Supadata] request failed: {response.status_code} - {response.text[:500]}"
            )
            return None

        data = response.json() or {}
        if data.get("jobId") and not data.get("content"):
            logger.info(f"[YT Supadata] async job_id={data.get('jobId')}")
            return self._poll_job(data["jobId"])
        return self._content_or_none(data.get("content"))

    def _poll_job(self, job_id: str) -> Optional[str]:
        started = time.time()
        while True:
            response = requests.get(
                f"{self.BASE_URL}/transcript/{job_id}",
                headers=self._headers(),
                timeout=30,
            )
            if response.status_code != 200:
                logger.warning(
                    f"[YT Supadata] poll failed: {response.status_code} - {response.text[:500]}"
                )
                return None
            data = response.json() or {}
            status = data.get("status")
            if status == "completed":
                logger.info("[YT Supadata] job completed")
                return self._content_or_none(data.get("content"))
            if status == "failed":
                logger.warning(f"[YT Supadata] job failed: {data.get('error')}")
                return None
            if time.time() - started > self.poll_timeout:
                logger.warning("[YT Supadata] poll timeout")
                return None
            logger.info(f"[YT Supadata] job status={status}")
            time.sleep(self.poll_interval)

    def _content_or_none(self, content: Any) -> Optional[str]:
        transcript = self.to_bracketed_transcript(content)
        if not transcript.strip():
            logger.warning("[YT Supadata] empty transcript")
            return None
        logger.info(f"[YT Supadata] transcript length={len(transcript)}")
        return transcript


def strip_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()
