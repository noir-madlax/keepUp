"""查询腾讯云中文语音识别任务状态（读取环境变量，不含硬编码密钥）。

用法：
  输入 TaskId，打印 JSON 并将结果写入 test-api/output/tencent_asr/<TaskId>.json。
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


def describe_task(task_id: int) -> dict:
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

    req = models.DescribeTaskStatusRequest()
    req.from_json_string(json.dumps({"TaskId": task_id}))

    resp = client.DescribeTaskStatus(req)
    return json.loads(resp.to_json_string())


if __name__ == "__main__":
    task_id_str = input("Enter Tencent ASR TaskId: ")
    task_id = int(task_id_str)
    data = describe_task(task_id)

    out_dir = Path("/Users/rigel/project/keepup-v2/backend/test-api/output/tencent_asr")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{task_id}.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved: {out_path}")