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

    @staticmethod
    async def polish_content(batch: str, workflow_id: str) -> dict:
        """调用 Coze API 润色内容批次
        
        Args:
            batch: 待润色的内容批次
            workflow_id: Coze 工作流 ID
            
        Returns:
            dict: Coze API 的响应结果
        """
        timeout = httpx.Timeout(300.0, connect=60.0)
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            logger.info(f"发送润色请求到 Coze API - Workflow: {workflow_id}")
            logger.info(f"待润色内容长度: {len(batch)} 字符")
            
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
                        "key0": batch,
                        "BOT_USER_INPUT": ""  # 保持一致性
                    }
                }
            )
            
            response.raise_for_status()
            result = response.json()
            logger.info(f"润色请求完成 - Token消耗: {result.get('cost', 'unknown')}")
            
            return result 

    @staticmethod
    async def process_detailed_content(content: str, workflow_id: str) -> dict:
        """调用 Coze API 处理分段详述内容
        
        Args:
            content: 待处理的内容
            workflow_id: Coze 工作流 ID
            
        Returns:
            dict: Coze API 的响应结果
        """
        timeout = httpx.Timeout(300.0, connect=60.0)
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            logger.info(f"发送分段详述请求到 Coze API - Workflow: {workflow_id}")
            logger.info(f"待处理内容长度: {len(content)} 字符")
            
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
                        "content": content,
                        "BOT_USER_INPUT": ""
                    }
                }
            )
            
            response.raise_for_status()
            result = response.json()
            logger.info(f"分段详述请求完成 - Token消耗: {result.get('cost', 'unknown')}")
            
            return result