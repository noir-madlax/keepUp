import httpx
from typing import Dict, AsyncGenerator
from app.config import settings
from app.utils.logger import logger
import json
from app.utils.sse import SSEMessage

class DeepseekService:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
    async def chat_stream(self, context: Dict) -> AsyncGenerator[str, None]:
        """流式调用 Deepseek API"""
        try:
            # 构建请求数据
            request_data = {
                "model": "qwen/qwen-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": context["prompt"]
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 1000,
                "timeout": 30,  
                 "provider": {
                    "order": [
                      "Fireworks",
                      "DeepInfra"
                    ],
                    "allow_fallbacks": False
                },
                "stream": True  # 启用流式响应，发版本更新3下
            }
            
            # 添加历史消息
            for msg in context["history"]:
                request_data["messages"].append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # 记录请求数据
            logger.info(f"Deepseek Request: {json.dumps(request_data, ensure_ascii=False)}")
            
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "Accept": "text/event-stream"
                    },
                    json=request_data,
                    timeout=120.0
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            if line.strip() == "data: [DONE]":
                                yield SSEMessage.create(content="", done=True)
                                break
                            
                            try:
                                data = json.loads(line[6:])
                                if content := data["choices"][0]["delta"].get("content"):
                                    # 使用统一的 SSE 消息格式
                                    yield SSEMessage.create(
                                        content=content,
                                        event_type="deepseek"
                                    )
                            except json.JSONDecodeError:
                                logger.error(f"Deepseek API JSON解析失败，原始数据为: {line}")
                                continue
                            except KeyError as e:
                                logger.error(f"Deepseek API 返回数据结构异常: {str(e)}, 数据: {data}")
                                continue
                    
        except Exception as e:
            logger.error(f"Deepseek API 调用失败: {str(e)}", exc_info=True)
            raise 
