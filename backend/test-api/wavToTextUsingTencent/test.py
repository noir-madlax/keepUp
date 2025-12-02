
import json
import os
import sys
import time
import base64
import subprocess
from pathlib import Path

# Add backend directory to sys.path to allow imports if needed, 
# though we will copy the class to be self-contained and modify it.
current_dir = Path(__file__).parent
backend_dir = current_dir.parent.parent.parent
sys.path.append(str(backend_dir))

from dotenv import load_dotenv
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.asr.v20190614 import asr_client, models

class LocalTencentASRClient:
    def __init__(self):
        # Load .env from backend root
        env_path = current_dir.parent.parent / ".env"
        print(f"Loading .env from: {env_path}")
        load_dotenv(dotenv_path=env_path)
        
        self.secret_id = os.getenv("TENCENTCLOUD_SECRET_ID")
        self.secret_key = os.getenv("TENCENTCLOUD_SECRET_KEY")
        if not self.secret_id or not self.secret_key:
            raise RuntimeError("Tencent Cloud credentials missing in .env")

        self.engine = os.getenv("TENCENT_ASR_ENGINE", "16k_zh")
        # self.poll_interval = int(os.getenv("TENCENT_POLL_INTERVAL", "5"))
        self.poll_interval = 2 # Faster polling for test
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

    def create_task(self, audio_data_base64: str, audio_format: str = "mp3") -> int:
        """
        Create ASR task using Data (base64) instead of URL.
        SourceType=1 means data.
        """
        req = models.CreateRecTaskRequest()
        params = {
            "EngineModelType": self.engine,
            "ChannelNum": 1,
            "ResTextFormat": 0,
            "SourceType": 1,  # 1: Data
            "Data": audio_data_base64,
            # If needed, specify format, but usually auto-detected or specified in filename?
            # CreateRecTask doesn't have "Format" field in params usually, it infers or uses "DataLen"?
            # Checking docs: CreateRecTask has `Data` and `DataLen` (optional). 
            # Actually, `Data` is the audio data.
            # Wait, the `params` structure depends on the SDK/API version.
            # In 20190614, parameters are: EngineModelType, ChannelNum, ResTextFormat, SourceType, Data/Url.
            # It doesn't explicitly ask for format in the top level usually? 
            # Ah, CreateRecTask docs say: "Data" - Base64 encoded audio.
            # There is no "Format" parameter? 
            # Actually, Tencent ASR usually supports wav/mp3/etc. automatically or via EngineModelType sometimes?
            # Wait, let's check the official docs or assume it works for mp3.
            # Standard CreateRecTask supports wav, pcm, ogg-opus, speex, silk, mp3, m4a, aac.
        }
        
        # Ensure data size is within limits (checked before calling this)
        
        req.from_json_string(json.dumps(params))
        try:
            resp = self.client.CreateRecTask(req)
            data = json.loads(resp.to_json_string())
            task_id = data.get("Data", {}).get("TaskId") or data.get("TaskId")
            if task_id is None:
                print(f"Full response: {data}")
                raise RuntimeError("Failed to create Tencent ASR task")
            return int(task_id)
        except Exception as e:
            print(f"Error creating task: {e}")
            raise

    def poll_result(self, task_id: int) -> dict:
        start = time.time()
        while True:
            req = models.DescribeTaskStatusRequest()
            req.from_json_string(json.dumps({"TaskId": int(task_id)}))
            resp = self.client.DescribeTaskStatus(req)
            data = json.loads(resp.to_json_string())
            status = data.get("Data", {}).get("StatusStr")
            
            # Print progress
            print(f"Task {task_id} status: {status}")
            
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
        data = result_json.get("Data", {})
        detail = data.get("ResultDetail")
        lines = []
        if isinstance(detail, list) and detail:
            for seg in detail:
                bg = seg.get("SliceStartTime", 0) / 1000.0
                text = seg.get("FinalSentence") or seg.get("Text") or ""
                ts = self._sec_to_hhmmss(bg)
                if text:
                    lines.append(f"[{ts}] {text.strip()}")
        else:
            plain = data.get("Result", "").strip()
            if plain:
                lines.append(f"[00:00:00] {plain}")
        return "\n".join(lines)

def convert_wav_to_mp3(input_path: Path, output_path: Path):
    """Convert wav to mp3 using ffmpeg to reduce size."""
    print(f"Converting {input_path} to {output_path}...")
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-codec:a", "libmp3lame", "-qscale:a", "4", # Variable bitrate, quality 4 (approx 128-160kbps)
        str(output_path)
    ]
    # Use lower bitrate if file is very large?
    # Let's try standard first.
    
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("Conversion complete.")

def main():
    # Target file
    input_wav = current_dir / "input" / "小仓广场.m4a"
    temp_mp3 = current_dir / "temp_audio.mp3"
    
    if not input_wav.exists():
        print(f"Error: File not found: {input_wav}")
        return

    # 1. Convert to MP3 to reduce size (target < 5MB)
    # Using very low bitrate for 7MB m4a file
    print("Compressing audio to meet API size limits (<5MB)...")
    cmd = [
        "ffmpeg", "-y", "-i", str(input_wav),
        "-codec:a", "libmp3lame", "-b:a", "24k", "-ac", "1",
        str(temp_mp3)
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg conversion failed: {e.stderr.decode()}")
        return

    # Check size
    file_size = temp_mp3.stat().st_size
    print(f"Compressed file size: {file_size / 1024 / 1024:.2f} MB")
    
    if file_size > 5 * 1024 * 1024:
        print("Error: Compressed file is still > 5MB. Cannot use Data upload method.")
        return

    # 2. Read and Encode
    with open(temp_mp3, "rb") as f:
        audio_data = f.read()
        base64_data = base64.b64encode(audio_data).decode("utf-8")

    # 3. Call API
    try:
        client = LocalTencentASRClient()
        print("Creating ASR task...")
        task_id = client.create_task(base64_data)
        print(f"Task created. ID: {task_id}")
        
        # 4. Poll Result
        print("Polling for result...")
        result = client.poll_result(task_id)
        
        # 5. Process Output
        transcript = client.to_bracketed_transcript(result)
        
        # Save to file
        output_dir = current_dir / "output"
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"{input_wav.stem}.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(transcript)
            
        print(f"\nSuccess! Transcript saved to: {output_file}")
        print("-" * 20)
        print(transcript[:500] + "..." if len(transcript) > 500 else transcript)
        
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        if temp_mp3.exists():
            os.remove(temp_mp3)

if __name__ == "__main__":
    main()

