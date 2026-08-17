"""Download YouTube audio and transcribe it with the production Tencent ASR path.

YouTube CDN URLs cannot be passed to Tencent (they require signed headers).
Production therefore downloads m4a locally, uploads to Supabase Storage
(`private-uploads`), and sends that public URL to CreateRecTask — the same
URL pattern used by private audio uploads.
"""
from __future__ import annotations

import asyncio
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from app.utils.logger import logger


class YouTubeAudioAsrProvider:
    """yt-dlp m4a download → Supabase public URL → Tencent ASR."""

    AUDIO_FORMAT = "140/bestaudio[ext=m4a]/bestaudio"
    PLAYER_CLIENT = "youtube:player_client=tv_embedded"

    def __init__(self) -> None:
        self.yt_dlp = shutil.which("yt-dlp") or "yt-dlp"
        self.node = shutil.which("node")
        self.ffmpeg = shutil.which("ffmpeg")

    def _webshare_proxy_urls(self) -> list[str]:
        """Return HTTP proxies that can fetch googlevideo (not Web Unlocker)."""
        token = os.getenv("WEBSHARE_API_TOKEN")
        if not token:
            try:
                from app.config import settings

                token = getattr(settings, "WEBSHARE_API_TOKEN", None)
            except Exception:
                token = None
        if not token:
            return []
        try:
            import requests

            resp = requests.get(
                "https://proxy.webshare.io/api/v2/proxy/list/",
                headers={"Authorization": f"Token {token}"},
                params={"mode": "direct", "page": 1, "page_size": 10},
                timeout=20,
            )
            resp.raise_for_status()
            results = resp.json().get("results") or []
        except Exception as e:
            logger.warning(f"[YT Audio ASR] webshare list failed: {type(e).__name__}")
            return []

        ranked = sorted(results, key=lambda item: 0 if item.get("country_code") == "US" else 1)
        urls: list[str] = []
        for item in ranked:
            user = item.get("username")
            password = item.get("password")
            address = item.get("proxy_address")
            port = item.get("port")
            if all([user, password, address, port]):
                urls.append(f"http://{user}:{password}@{address}:{port}")
        return urls

    def _base_cmd(self, out_tmpl: str) -> list[str]:
        return [
            self.yt_dlp,
            "--js-runtimes",
            f"node:{self.node}",
            "--impersonate",
            "chrome",
            "--extractor-args",
            self.PLAYER_CLIENT,
            "-f",
            self.AUDIO_FORMAT,
            "-o",
            out_tmpl,
            "--no-playlist",
            "--no-warnings",
        ]

    def _download_audio(self, video_url: str, dest_dir: str) -> str:
        if not self.node:
            raise RuntimeError("Node.js >= 22 is required for yt-dlp YouTube downloads")
        if not self.ffmpeg:
            logger.warning("[YT Audio ASR] ffmpeg not found; m4a container fixup may fail")

        out_tmpl = str(Path(dest_dir) / "audio.%(ext)s")
        proxies = self._webshare_proxy_urls()
        if not proxies:
            logger.warning("[YT Audio ASR] no Webshare proxies; trying direct download")
            proxies = [None]

        timeout = int(os.getenv("YOUTUBE_AUDIO_DOWNLOAD_TIMEOUT", "300"))
        last_err = "yt-dlp failed"
        for proxy_url in proxies[:5]:
            cmd = self._base_cmd(out_tmpl)
            if proxy_url:
                cmd.extend(["--proxy", proxy_url])
                logger.info("[YT Audio ASR] yt-dlp webshare proxy enabled")
            cmd.append(video_url)
            logger.info(f"[YT Audio ASR] download start url={video_url}")
            completed = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            err = (completed.stderr or completed.stdout or "").strip()
            if proxy_url:
                err = err.replace(proxy_url, "[proxy]")
            if completed.returncode == 0:
                files = [
                    path
                    for path in Path(dest_dir).glob("audio.*")
                    if path.is_file() and path.stat().st_size > 0
                ]
                if files:
                    audio_path = str(files[0])
                    logger.info(
                        f"[YT Audio ASR] download ok path={audio_path} size={os.path.getsize(audio_path)}"
                    )
                    return audio_path
                last_err = "yt-dlp finished but produced no audio file"
            else:
                last_err = err[-800:] or last_err
                logger.warning("[YT Audio ASR] yt-dlp attempt failed, trying next proxy")
            for leftover in Path(dest_dir).glob("audio.*"):
                leftover.unlink(missing_ok=True)

        raise RuntimeError(f"yt-dlp failed: {last_err}")

    async def transcribe(self, video_url: str, user_id: str) -> Optional[str]:
        dest_dir = tempfile.mkdtemp(prefix="yt-asr-")
        try:
            audio_path = await asyncio.to_thread(self._download_audio, video_url, dest_dir)
            with open(audio_path, "rb") as fh:
                audio_bytes = fh.read()
            filename = Path(audio_path).name
            from app.services.private_content_service import PrivateContentService

            public_url = await PrivateContentService.upload_audio_to_storage(
                audio_bytes, filename, user_id or "youtube-asr"
            )
            if not public_url:
                logger.error("[YT Audio ASR] supabase upload returned empty URL")
                return None
            logger.info(f"[YT Audio ASR] public_url={public_url}")

            def _run_asr(url: str) -> str:
                from app.services.transcript.tencent_asr import TencentASRClient

                asr = TencentASRClient()
                task_id = asr.create_task(url)
                logger.info(f"[YT Audio ASR] tencent task_id={task_id}")
                result = asr.poll_result(task_id)
                status = (result.get("Data") or {}).get("StatusStr")
                logger.info(f"[YT Audio ASR] tencent status={status}")
                if status != "success":
                    raise RuntimeError(f"Tencent ASR status={status}")
                return asr.to_bracketed_transcript(result)

            transcript = await asyncio.to_thread(_run_asr, public_url)
            if not transcript or not transcript.strip():
                logger.warning("[YT Audio ASR] empty transcript")
                return None
            logger.info(f"[YT Audio ASR] transcript length={len(transcript)}")
            return transcript
        except Exception as e:
            logger.exception(f"[YT Audio ASR] failed: {e}")
            return None
        finally:
            shutil.rmtree(dest_dir, ignore_errors=True)
