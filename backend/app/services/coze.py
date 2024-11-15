import httpx
from app.config import settings
from app.utils.logger import logger

class CozeService:
    @staticmethod
    async def parse_content(url: str, content: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.coze.com/v1/workflow/run",
                headers={
                    "Authorization": f"Bearer {settings.COZE_API_TOKEN}",
                    "Content-Type": "application/json",
                },
                json={
                    "workflow_id": settings.COZE_WORKFLOW_ID,
                    "parameters": {
                        "BOT_USER_INPUT": "",
                        "timestamp": None,
                        "link": url,
                        "content": content or ""
                    }
                }
            )
            response.raise_for_status()
            return response.json() 