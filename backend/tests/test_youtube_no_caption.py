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


class YoutubeAudioDownloadCommandTest(unittest.TestCase):
    def test_download_invokes_yt_dlp_with_node_runtime(self):
        from app.services.transcript.youtube_audio import YouTubeAudioAsrProvider

        provider = YouTubeAudioAsrProvider()
        provider.yt_dlp = "/usr/bin/yt-dlp"
        provider.node = "/usr/bin/node"
        provider.ffmpeg = "/usr/bin/ffmpeg"

        with patch("app.services.transcript.youtube_audio.subprocess.run") as run:
            run.return_value = MagicMock(returncode=0, stderr="", stdout="")
            with patch("app.services.transcript.youtube_audio.Path.glob", return_value=[]):
                with self.assertRaises(RuntimeError):
                    provider._download_audio("https://www.youtube.com/watch?v=toRqAY3xp4A", "/tmp/x")
            cmd = run.call_args[0][0]
            self.assertEqual(cmd[0], "/usr/bin/yt-dlp")
            self.assertIn("--js-runtimes", cmd)
            self.assertIn("node:/usr/bin/node", cmd)
            self.assertIn("140/bestaudio[ext=m4a]/bestaudio", cmd)


class YoutubeFetchFailClosedTest(unittest.IsolatedAsyncioTestCase):
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
            "app.services.content_fetcher.youtube.YouTubeAudioAsrProvider"
        ) as provider_cls:
            provider_cls.return_value.transcribe = AsyncMock(return_value=None)
            result = await fetcher.fetch("https://www.youtube.com/watch?v=toRqAY3xp4A")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
