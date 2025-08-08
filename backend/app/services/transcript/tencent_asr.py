import json
import math
import os
import time
from datetime import timedelta
from typing import Optional

from dotenv import load_dotenv
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.asr.v20190614 import asr_client, models


class TencentASRClient:
    def __init__(self):
        load_dotenv(dotenv_path="/Users/rigel/project/keepup-v2/backend/.env")
        self.secret_id = os.getenv("TENCENTCLOUD_SECRET_ID")
        self.secret_key = os.getenv("TENCENTCLOUD_SECRET_KEY")
        if not self.secret_id or not self.secret_key:
            raise RuntimeError("Tencent Cloud credentials missing in .env")

        self.engine = os.getenv("TENCENT_ASR_ENGINE", "16k_zh")
        self.poll_interval = int(os.getenv("TENCENT_POLL_INTERVAL", "5"))
        self.poll_timeout = int(os.getenv("TENCENT_POLL_TIMEOUT", "3600"))

        http = HttpProfile()
        http.endpoint = "asr.tencentcloudapi.com"
        client_profile = ClientProfile()
        client_profile.httpProfile = http
        self.client = asr_client.AsrClient(
            credential.Credential(self.secret_id, self.secret_key),
            "",
            client_profile,
        )

    def create_task(self, audio_url: str) -> int:
        req = models.CreateRecTaskRequest()
        params = {
            "Url": audio_url,
            "ChannelNum": 1,
            "EngineModelType": self.engine,
            "ResTextFormat": 0,
            "SourceType": 0,
        }
        req.from_json_string(json.dumps(params))
        resp = self.client.CreateRecTask(req)
        data = json.loads(resp.to_json_string())
        task_id = data.get("Data", {}).get("TaskId") or data.get("TaskId")
        if task_id is None:
            raise RuntimeError("Failed to create Tencent ASR task")
        return int(task_id)

    def poll_result(self, task_id: int) -> dict:
        start = time.time()
        while True:
            req = models.DescribeTaskStatusRequest()
            req.from_json_string(json.dumps({"TaskId": int(task_id)}))
            resp = self.client.DescribeTaskStatus(req)
            data = json.loads(resp.to_json_string())
            status = data.get("Data", {}).get("StatusStr")
            if status in ("success", "failed", "slice_error"):
                return data
            if time.time() - start > self.poll_timeout:
                raise TimeoutError("Tencent ASR polling timeout")
            time.sleep(self.poll_interval)

    @staticmethod
    def _sec_to_hhmmss(seconds: float) -> str:
        if seconds < 0:
            seconds = 0
        total = int(seconds)
        h = total // 3600
        m = (total % 3600) // 60
        s = total % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    def to_bracketed_transcript(self, result_json: dict) -> str:
        """Convert Tencent result to lines like: [hh:mm:ss] text

        Tencent Data.Result can be a long string or detailed structure depending on config.
        We handle the common slice format found in DescribeTaskStatus.
        """
        data = result_json.get("Data", {})
        detail = data.get("ResultDetail")
        # If detailed segments available
        lines = []
        if isinstance(detail, list) and detail:
            for seg in detail:
                bg = seg.get("SliceStartTime", 0) / 1000.0
                text = seg.get("FinalSentence") or seg.get("Text") or ""
                ts = self._sec_to_hhmmss(bg)
                if text:
                    lines.append(f"[{ts}] {text.strip()}")
        else:
            # fallback: use Result plain text without timestamps
            plain = data.get("Result", "").strip()
            if plain:
                lines.append(f"[00:00:00] {plain}")
        return "\n".join(lines)


