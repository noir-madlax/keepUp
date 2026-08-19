import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Settings is constructed at import time; tests do not use real secrets.
_TEST_ENV = {
    "log_level": "INFO",
    "SUPABASE_URL": "https://example.supabase.co",
    "SUPABASE_SERVICE_ROLE_KEY": "test-service-role",
    "WEBSHARE_API_TOKEN": "x",
    "COZE_API_TOKEN": "x",
    "COZE_WORKFLOW_ID_ZH": "x",
    "COZE_WORKFLOW_ID_EN": "x",
    "COZE_POLISH_WORKFLOW_ID_ZH": "x",
    "COZE_POLISH_WORKFLOW_ID_EN": "x",
    "COZE_DETAILED_WORKFLOW_ID_ZH": "x",
    "COZE_DETAILED_WORKFLOW_ID_EN": "x",
    "COZE_WEB_SUMMARY_ID_ZH": "x",
    "COZE_WEB_SUMMARY_ID_EN": "x",
    "COZE_FILE_SUMMARY_ID_ZH": "x",
    "COZE_FILE_SUMMARY_ID_EN": "x",
    "ASSEMBLYAI_API_KEY": "x",
    "SERPAPI_KEY": "x",
    "DEEPSEEK_API_KEY": "x",
    "OPENROUTER_API_KEY": "x",
    "DAJIALA_KEY": "x",
    "DAJIALA_VERIFYCODE": "x",
    "AWS_ACCESS_KEY_ID": "x",
    "AWS_SECRET_ACCESS_KEY": "x",
    "USE_PROXY": "false",
}
os.environ.update(_TEST_ENV)

from app.services.transcript.text_utils import strip_inner_timestamps, build_youtube_content


class StripInnerTimestampsTest(unittest.TestCase):
    def test_strips_tencent_slice_prefix(self):
        raw = "[0:0.000,1:0.300]  大家好，我是布鲁斯"
        self.assertEqual(strip_inner_timestamps(raw), "大家好，我是布鲁斯")

    def test_keeps_plain_sentence(self):
        self.assertEqual(strip_inner_timestamps("深蹲时骨盆后倾"), "深蹲时骨盆后倾")

    def test_empty(self):
        self.assertEqual(strip_inner_timestamps(""), "")
        self.assertEqual(strip_inner_timestamps(None), "")  # type: ignore[arg-type]


class BuildYoutubeContentTest(unittest.TestCase):
    def test_returns_none_without_transcript(self):
        self.assertIsNone(build_youtube_content("title", {"name": "a"}, "desc", None))
        self.assertIsNone(build_youtube_content("title", {"name": "a"}, "desc", "   "))

    def test_includes_transcript_marker(self):
        content = build_youtube_content("T", {"name": "A"}, "D", "[00:00:00] hello")
        self.assertIsNotNone(content)
        self.assertIn("标题: T", content)
        self.assertIn("描述: D", content)
        self.assertIn("转录内容: [00:00:00] hello", content)


class MsToHhmmssTest(unittest.TestCase):
    def test_zero(self):
        from app.services.transcript.text_utils import ms_to_hhmmss

        self.assertEqual(ms_to_hhmmss(0), "00:00:00")

    def test_minutes_and_seconds(self):
        from app.services.transcript.text_utils import ms_to_hhmmss

        self.assertEqual(ms_to_hhmmss(8150), "00:00:08")
        self.assertEqual(ms_to_hhmmss(75_000), "00:01:15")


class SupadataTranscriptClientTest(unittest.TestCase):
    def test_chunks_to_bracketed(self):
        from app.services.transcript.supadata import SupadataTranscriptClient

        text = SupadataTranscriptClient.to_bracketed_transcript(
            [
                {"text": "hello", "offset": 0, "duration": 1000},
                {"text": "world", "offset": 8150, "duration": 1200},
            ]
        )
        self.assertEqual(text, "[00:00:00] hello\n[00:00:08] world")

    def test_plain_string_content(self):
        from app.services.transcript.supadata import SupadataTranscriptClient

        text = SupadataTranscriptClient.to_bracketed_transcript("hello world")
        self.assertEqual(text, "[00:00:00] hello world")

    def test_empty_content(self):
        from app.services.transcript.supadata import SupadataTranscriptClient

        self.assertEqual(SupadataTranscriptClient.to_bracketed_transcript([]), "")
        self.assertEqual(SupadataTranscriptClient.to_bracketed_transcript(""), "")

    def test_missing_key_returns_none(self):
        from app.services.transcript.supadata import SupadataTranscriptClient

        client = SupadataTranscriptClient()
        client.api_key = None
        self.assertIsNone(client.transcribe("https://www.youtube.com/watch?v=toRqAY3xp4A"))

    def test_mode_auto_immediate_200(self):
        from app.services.transcript.supadata import SupadataTranscriptClient

        client = SupadataTranscriptClient()
        client.api_key = "test-key"
        payload = {
            "content": [{"text": "深蹲", "offset": 0, "duration": 1200, "lang": "zh"}],
            "lang": "zh",
        }
        with patch("app.services.transcript.supadata.requests.get") as get:
            get.return_value = MagicMock(status_code=200, json=lambda: payload, text="")
            result = client.transcribe("https://www.youtube.com/watch?v=toRqAY3xp4A", "auto")
        self.assertEqual(result, "[00:00:00] 深蹲")
        args, kwargs = get.call_args
        self.assertIn("/transcript", args[0])
        self.assertEqual(kwargs["params"]["mode"], "auto")
        self.assertEqual(kwargs["params"]["text"], "false")

    def test_polls_202_job_until_completed(self):
        from app.services.transcript.supadata import SupadataTranscriptClient

        client = SupadataTranscriptClient()
        client.api_key = "test-key"
        client.poll_interval = 0
        queued = MagicMock(status_code=202, json=lambda: {"jobId": "job-1"}, text="")
        pending = MagicMock(status_code=200, json=lambda: {"status": "active"}, text="")
        done = MagicMock(
            status_code=200,
            json=lambda: {
                "status": "completed",
                "content": [{"text": "hello", "offset": 1000, "duration": 500}],
            },
            text="",
        )
        with patch("app.services.transcript.supadata.requests.get", side_effect=[queued, pending, done]):
            result = client.transcribe("https://www.youtube.com/watch?v=xxqFoBHD9UE")
        self.assertEqual(result, "[00:00:01] hello")


class YoutubeFetchFailClosedTest(unittest.IsolatedAsyncioTestCase):
    async def test_fetch_uses_captions_and_skips_audio_asr(self):
        try:
            from app.services.content_fetcher.youtube import YouTubeFetcher
            from app.services.content_fetcher.base import VideoInfo
        except ImportError as e:
            self.skipTest(f"youtube fetcher deps missing: {e}")

        fetcher = YouTubeFetcher.__new__(YouTubeFetcher)
        video = VideoInfo.model_construct(
            title="t",
            description="d",
            author={"name": "a"},
            article=None,
        )
        fetcher.get_video_info = AsyncMock(return_value=video)
        fetcher._extract_video_id = MagicMock(return_value="IFvLorAL5-8")
        fetcher._get_transcript = AsyncMock(return_value="[00:00:00] caption text")
        fetcher._select_fallback_podcast_url = AsyncMock()

        with patch(
            "app.services.content_fetcher.youtube.SupadataTranscriptClient"
        ) as provider_cls:
            result = await fetcher.fetch("https://www.youtube.com/watch?v=IFvLorAL5-8")

        provider_cls.assert_not_called()
        fetcher._select_fallback_podcast_url.assert_not_called()
        self.assertIsNotNone(result)
        self.assertIn("转录内容: [00:00:00] caption text", result)

    async def test_fetch_returns_none_when_all_transcripts_fail(self):
        try:
            from app.services.content_fetcher.youtube import YouTubeFetcher
            from app.services.content_fetcher.base import VideoInfo
        except ImportError as e:
            self.skipTest(f"youtube fetcher deps missing: {e}")

        fetcher = YouTubeFetcher.__new__(YouTubeFetcher)
        video = VideoInfo.model_construct(
            title="t",
            description="d",
            author={"name": "a"},
            article=None,
        )
        fetcher.get_video_info = AsyncMock(return_value=video)
        fetcher._extract_video_id = MagicMock(return_value="toRqAY3xp4A")
        fetcher._get_transcript = AsyncMock(return_value=None)
        fetcher._select_fallback_podcast_url = AsyncMock(return_value=(None, None, ""))

        with patch(
            "app.services.content_fetcher.youtube.SupadataTranscriptClient"
        ) as provider_cls:
            provider_cls.return_value.transcribe = MagicMock(return_value=None)
            result = await fetcher.fetch("https://www.youtube.com/watch?v=toRqAY3xp4A")
        provider_cls.assert_called_once()
        self.assertIsNone(result)

    async def test_fetch_uses_supadata_whisper_when_captions_empty(self):
        try:
            from app.services.content_fetcher.youtube import YouTubeFetcher
            from app.services.content_fetcher.base import VideoInfo
        except ImportError as e:
            self.skipTest(f"youtube fetcher deps missing: {e}")

        fetcher = YouTubeFetcher.__new__(YouTubeFetcher)
        video = VideoInfo.model_construct(
            title="t",
            description="d",
            author={"name": "a"},
            article=None,
        )
        fetcher.get_video_info = AsyncMock(return_value=video)
        fetcher._extract_video_id = MagicMock(return_value="NESeTg2-9bk")
        fetcher._get_transcript = AsyncMock(return_value=None)
        fetcher._select_fallback_podcast_url = AsyncMock(return_value=(None, None, ""))

        with patch(
            "app.services.content_fetcher.youtube.SupadataTranscriptClient"
        ) as provider_cls:
            provider_cls.return_value.transcribe = MagicMock(
                return_value="[00:00:00] generated speech"
            )
            result = await fetcher.fetch("https://www.youtube.com/watch?v=NESeTg2-9bk")
        self.assertIsNotNone(result)
        self.assertIn("转录内容: [00:00:00] generated speech", result)


if __name__ == "__main__":
    unittest.main()
