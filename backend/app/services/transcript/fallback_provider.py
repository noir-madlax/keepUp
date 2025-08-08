import os
from typing import Optional

from dotenv import load_dotenv

from .xiaoyuzhou_resolver import XiaoYuZhouResolver
from .tencent_asr import TencentASRClient


class TranscriptFallbackProvider:
    """Provide transcript via XiaoYuZhou + Tencent ASR when YouTube captions are missing."""

    def __init__(self):
        load_dotenv(dotenv_path="/Users/rigel/project/keepup-v2/backend/.env")
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
        audio_url = self.resolver.find_episode_audio(podcast_url, title)
        if not audio_url:
            return None
        task_id = self.asr.create_task(audio_url)
        result = self.asr.poll_result(task_id)
        return self.asr.to_bracketed_transcript(result)


