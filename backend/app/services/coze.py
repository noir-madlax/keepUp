import httpx
from app.config import settings
from app.utils.logger import logger

class CozeService:
    @staticmethod
    async def parse_content(url: str, content: str, chapters: str, workflow_id: str) -> dict:
        # 设置超时时间为 5 分钟 (300 秒)
        timeout = httpx.Timeout(300.0, connect=60.0)
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            logger.info(f"发送请求到 Coze API - URL: {url}, Workflow: {workflow_id}")
            response = await client.post(
                "https://api.coze.com/v1/workflow/run",
                headers={
                    "Authorization": f"Bearer {settings.COZE_API_TOKEN}",
                    "Content-Type": "application/json",
                    "Accept": "*/*",
                    "Host": "api.coze.com",
                    "Connection": "keep-alive"
                },
                json={
                    "workflow_id": workflow_id,
                    "parameters": {
                        "BOT_USER_INPUT": "",
                        "timestamp": chapters,
                        "link": url,
                        "content": content or ""
                    }
                }
            )
            response.raise_for_status()
            return response.json() 