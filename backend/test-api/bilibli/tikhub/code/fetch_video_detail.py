import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Setup paths
current_dir = Path(__file__).parent
output_dir = current_dir.parent / "output"
output_dir.mkdir(parents=True, exist_ok=True)
env_path = Path(__file__).parents[4] / ".env"
load_dotenv(env_path)
TIKHUB_KEY = os.getenv("tikhub_KEY")

def main():
    endpoint = "fetch_video_detail"
    url = f"https://api.tikhub.io/api/v1/bilibili/web/{endpoint}"
    
    aid = "115014593680988" # From previous output
    
    print(f"Testing {endpoint} with aid={aid}")
    
    headers = {"Authorization": f"Bearer {TIKHUB_KEY}"}
    params = {"aid": aid}
    
    try:
        resp = requests.get(url, headers=headers, params=params)
        result = resp.json()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"response_{endpoint}_{timestamp}.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        print(f"Saved to {output_file}")
        print(json.dumps(result, ensure_ascii=False, indent=2)[:200])
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

