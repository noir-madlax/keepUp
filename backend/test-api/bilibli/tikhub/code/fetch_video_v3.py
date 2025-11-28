import os
import json
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Setup paths
current_dir = Path(__file__).parent
output_dir = current_dir.parent / "output"
output_dir.mkdir(parents=True, exist_ok=True)

# Assuming .env is in backend/
env_path = Path(__file__).parents[4] / ".env"

# Load env
load_dotenv(env_path)
TIKHUB_KEY = os.getenv("tikhub_KEY")

def fetch_tikhub_video_v3(video_url, token):
    """Call TikHub API V3"""
    url = "https://api.tikhub.io/api/v1/bilibili/web/fetch_one_video_v3"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "url": video_url
    }
    print(f"Calling TikHub V3 with url={video_url}")
    resp = requests.get(url, headers=headers, params=params)
    return resp.json()

def main():
    # 使用用户之前提供的链接
    video_url = "https://www.bilibili.com/video/BV1AbsqzxEqs/?spm_id_from=333.337.search-card.all.click&vd_source=3d1a30968b278a2beb02c0503f296200"
    
    print(f"Processing URL: {video_url}")
    
    if not TIKHUB_KEY:
        print("Error: tikhub_KEY not found in environment")
        if "tikhub_KEY" in os.environ:
            print("Found tikhub_KEY in os.environ")
        else:
            print("Please ensure tikhub_KEY is set in .env")
            return

    # Call TikHub V3
    result = fetch_tikhub_video_v3(video_url=video_url, token=TIKHUB_KEY)
    
    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"response_v3_{timestamp}.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Saved result to {output_file}")
    print("-" * 50)
    
    # Print a snippet of the result
    print(json.dumps(result, ensure_ascii=False, indent=2)[:500] + "...")

if __name__ == "__main__":
    main()
