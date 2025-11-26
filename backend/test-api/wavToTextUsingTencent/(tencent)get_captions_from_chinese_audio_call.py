"""创建腾讯云中文语音识别任务（读取环境变量），传入音频 URL。

用法：
  交互式输入音频 URL，创建任务后打印 TaskId 并保存 JSON 到 test-api/output/tencent_asr/create_<TaskId>.json
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.asr.v20190614 import asr_client, models


def create_task(audio_url: str, engine_model_type: str = "16k_zh") -> dict:
    # 加载 backend/.env
    load_dotenv(dotenv_path="/Users/rigel/project/keepup-v2/backend/.env")
    secret_id = os.getenv("TENCENTCLOUD_SECRET_ID")
    secret_key = os.getenv("TENCENTCLOUD_SECRET_KEY")
    if not secret_id or not secret_key:
        raise RuntimeError("Tencent Cloud credentials are not set in environment variables.")

    http_profile = HttpProfile()
    http_profile.endpoint = "asr.tencentcloudapi.com"

    client_profile = ClientProfile()
    client_profile.httpProfile = http_profile

    client = asr_client.AsrClient(credential.Credential(secret_id, secret_key), "", client_profile)

    req = models.CreateRecTaskRequest()
    params = {
        "Url": audio_url,
        "ChannelNum": 1,
        "EngineModelType": engine_model_type,
        "ResTextFormat": 0,
        "SourceType": 0,
    }
    req.from_json_string(json.dumps(params))

    resp = client.CreateRecTask(req)
    return json.loads(resp.to_json_string())


if __name__ == "__main__":
    url = input("Enter audio URL: ")
    data = create_task(url)
    print("CreateRecTask Response:", data)

    task_id = data.get("Data", {}).get("TaskId") or data.get("TaskId")
    if task_id is not None:
        out_dir = Path("/Users/rigel/project/keepup-v2/backend/test-api/output/tencent_asr")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"create_{task_id}.json"
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved: {out_path}")
        print(f"TaskId: {task_id}")
    else:
        print("Failed to parse TaskId from response.")