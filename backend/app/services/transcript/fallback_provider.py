import os
from typing import Optional

from dotenv import load_dotenv
from app.utils.logger import logger

from .xiaoyuzhou_resolver import XiaoYuZhouResolver
from .tencent_asr import TencentASRClient


class TranscriptFallbackProvider:
    """Provide transcript via XiaoYuZhou + Tencent ASR when YouTube captions are missing."""

    def __init__(self):
        try:
            load_dotenv(dotenv_path="/Users/rigel/project/keepup-v2/backend/.env")
        except Exception:
            pass
        self.resolver = XiaoYuZhouResolver()
        self.asr = TencentASRClient()

    def _select_podcast_url(self, channel_handle_or_name: str) -> Optional[str]:
        mapping = os.getenv("YOUTUBE_FALLBACK_CHANNEL_MAP", "")
        pairs = [p for p in mapping.split(",") if p.strip()]
        for p in pairs:
            if "=" in p:
                key, val = p.split("=", 1)
                if key.strip().lower() in channel_handle_or_name.lower():
                    return val.strip()
        return None

    async def transcribe_from_xiaoyuzhou(self, title: str, podcast_url: str) -> Optional[str]:
        logger.info(f"[XZ Fallback] Start resolve audio by title. podcast_url='{podcast_url}' title='{title[:80]}'")
        audio_url = self.resolver.find_episode_audio(podcast_url, title)
        if not audio_url:
            logger.warning("[XZ Fallback] No matched episode audio url found.")
            return None
        logger.info(f"[XZ Fallback] Resolved audio_url: {audio_url}")
        task_id = self.asr.create_task(audio_url)
        logger.info(f"[XZ Fallback] Tencent ASR task created. task_id={task_id}")
        result = self.asr.poll_result(task_id)
        status = (result.get('Data') or {}).get('StatusStr')
        logger.info(f"[XZ Fallback] Tencent ASR task finished. status={status}")
        text = self.asr.to_bracketed_transcript(result)
        logger.info(f"[XZ Fallback] Transcript length={len(text) if text else 0}")
        return text


