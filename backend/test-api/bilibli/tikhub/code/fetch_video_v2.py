import os
import re
import json
import requests
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

def extract_bvid(url):
    """Extract BVID from URL"""
    match = re.search(r'(BV\w+)', url)
    return match.group(1) if match else None

def get_bilibili_info(bvid):
    """Get aid and cid from Bilibili API"""
    api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        print(f"Fetching info from Bilibili API for {bvid}...")
        resp = requests.get(api_url, headers=headers)
        data = resp.json()
        if data['code'] == 0:
            return data['data']
        else:
            print(f"Error getting Bilibili info: {data}")
            return None
    except Exception as e:
        print(f"Exception getting Bilibili info: {e}")
        return None

def fetch_tikhub_video(a_id, c_id, token):
    """Call TikHub API"""
    url = "https://api.tikhub.io/api/v1/bilibili/web/fetch_one_video_v2"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    # Note: a_id in TikHub likely corresponds to Bilibili aid (numeric), but let's see.
    params = {
        "a_id": a_id,
        "c_id": c_id
    }
    print(f"Calling TikHub with a_id={a_id}, c_id={c_id}")
    resp = requests.get(url, headers=headers, params=params)
    return resp.json()

def main():
    video_url = "https://www.bilibili.com/video/BV1AbsqzxEqs/?spm_id_from=333.337.search-card.all.click&vd_source=3d1a30968b278a2beb02c0503f296200"
    
    print(f"Processing URL: {video_url}")
    
    # 1. Extract BVID
    bvid = extract_bvid(video_url)
    if not bvid:
        print("Could not extract BVID from URL")
        return
    print(f"Extracted BVID: {bvid}")
    
    # 2. Get CID (and numeric AID) from Bilibili
    # We need CID for TikHub. The URL doesn't have it.
    bili_info = get_bilibili_info(bvid)
    if not bili_info:
        print("Could not fetch Bilibili info")
        return
        
    aid = bili_info['aid']
    cid = bili_info['cid']
    print(f"Got from Bilibili: aid={aid} (Numeric Work ID), cid={cid}")
    
    if not TIKHUB_KEY:
        print("Error: tikhub_KEY not found in environment")
        # Attempt to read from env var directly if dotenv failed (e.g. if running in a shell that has it)
        if "tikhub_KEY" in os.environ:
            print("Found tikhub_KEY in os.environ")
        else:
            print("Please ensure tikhub_KEY is set in .env")
            return

    # 3. Call TikHub
    # User asked: "is BV1hSt9zdEmX this the work id?"
    # Answer: BV... is the BVID. 'aid' is the numeric AV ID. 
    # The TikHub documentation 'a_id' example is numeric, so it likely expects the numeric 'aid'.
    # We will use the numeric aid extracted from Bilibili.
    
    result = fetch_tikhub_video(a_id=aid, c_id=cid, token=TIKHUB_KEY)
    
    # 4. Save output
    output_file = output_dir / "response.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Saved result to {output_file}")
    print("-" * 50)
    # Print a snippet of the result
    print(json.dumps(result, ensure_ascii=False, indent=2)[:500] + "...")

if __name__ == "__main__":
    main()

