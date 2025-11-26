import requests
import os
import sys

# Add backend to sys.path to import settings
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../backend')))

from app.config import settings

def list_models():
    api_key = settings.OPENROUTER_API_KEY
    if not api_key:
        print("Error: OPENROUTER_API_KEY not found in settings")
        return

    url = "https://openrouter.ai/api/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print("Available Gemini models:")
        for model in data.get('data', []):
            if 'gemini' in model['id'].lower():
                print(f"- {model['id']}")
                
    except Exception as e:
        print(f"Error fetching models: {e}")

if __name__ == "__main__":
    list_models()

