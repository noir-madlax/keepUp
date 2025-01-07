import httpx
from typing import Dict
from app.config import settings
from app.utils.logger import logger
import json

class DeepseekService:
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        
    async def chat(self, context: Dict) -> str:
        """调用 Deepseek API"""
        try:
            # 构建请求数据
            request_data = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": context["prompt"]
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 1000,
                "stream": False
            }
            
            # 添加历史消息
            for msg in context["history"]:
                request_data["messages"].append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # 记录请求数据(单行)
            logger.info(f"Deepseek Request: {json.dumps(request_data, ensure_ascii=False)}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=request_data,
                    timeout=120.0
                )
                
                response.raise_for_status()
                result = response.json()
                
                # 记录响应数据(单行)
                logger.info(f"Deepseek Response: {json.dumps(result, ensure_ascii=False)}")
                
                # 从响应中提取助手的回复
                assistant_message = result["choices"][0]["message"]["content"]
                return assistant_message
                
        except Exception as e:
            logger.error(f"Deepseek API 调用失败: {str(e)}", exc_info=True)
            raise 