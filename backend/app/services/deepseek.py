import httpx
import boto3
import json
from botocore.config import Config
from typing import Dict, AsyncGenerator
from app.config import settings
from app.utils.logger import logger
from app.utils.sse import SSEMessage

class DeepseekService:
    # OpenRouter 配置
    OPENROUTER_MODEL = "google/gemini-2.5-flash"
    
    # AWS Bedrock 配置
    BEDROCK_MODEL = "us.anthropic.claude-haiku-4-5-20251001-v1:0"  # Claude Haiku 4.5
    BEDROCK_REGION = settings.AWS_BEDROCK_REGION
    BEDROCK_MAX_TOKENS = 4096
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
    async def chat_stream(self, context: Dict) -> AsyncGenerator[str, None]:
        """流式调用 Chat API，根据配置选择Provider"""
        provider = settings.LLM_CHAT_PROVIDER
        logger.info(f"Chat使用 {provider} 进行流式响应")
        
        if provider == "bedrock":
            async for chunk in self._chat_stream_bedrock(context):
                yield chunk
        else:
            async for chunk in self._chat_stream_openrouter(context):
                yield chunk
    
    async def _chat_stream_bedrock(self, context: Dict) -> AsyncGenerator[str, None]:
        """流式调用 AWS Bedrock API (Claude Haiku 4.5)"""
        try:
            # 配置超时时间
            config = Config(
                read_timeout=120,
                connect_timeout=30,
                retries={'max_attempts': 3}
            )
            
            # 创建Bedrock客户端
            bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name=self.BEDROCK_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                config=config
            )
            
            # 构建消息列表
            messages = []
            for msg in context["history"]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # 构建请求数据
            request_data = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.BEDROCK_MAX_TOKENS,
                "temperature": 0.1,
                "system": context["prompt"],  # system prompt
                "messages": messages
            }
            
            logger.info(f"正在调用Bedrock Haiku流式API...")
            logger.info(f"模型: {self.BEDROCK_MODEL}")
            
            # 调用Bedrock流式API
            response = bedrock_client.invoke_model_with_response_stream(
                modelId=self.BEDROCK_MODEL,
                body=json.dumps(request_data),
                contentType="application/json"
            )
            
            # 处理流式响应
            for event in response['body']:
                if 'chunk' in event:
                    chunk_data = json.loads(event['chunk']['bytes'].decode('utf-8'))
                    
                    # 处理不同类型的事件
                    if chunk_data.get('type') == 'content_block_delta':
                        delta = chunk_data.get('delta', {})
                        if delta.get('type') == 'text_delta':
                            text = delta.get('text', '')
                            if text:
                                yield SSEMessage.create(
                                    content=text,
                                    event_type="bedrock"
                                )
                    
                    # 处理结束事件
                    elif chunk_data.get('type') == 'message_stop':
                        yield SSEMessage.create(content="", done=True)
                        break
                        
        except Exception as e:
            logger.error(f"Bedrock Chat API 调用失败: {str(e)}", exc_info=True)
            raise
    
    async def _chat_stream_openrouter(self, context: Dict) -> AsyncGenerator[str, None]:
        """流式调用 OpenRouter API (Gemini Flash) - 原有实现"""
        try:
            # 构建请求数据
            request_data = {
                "model": self.OPENROUTER_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": context["prompt"]
                    }
                ],
                "temperature": 0.1,
                "timeout": 30,  
                "stream": True
            }
            
            # 添加历史消息
            for msg in context["history"]:
                request_data["messages"].append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
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
                                    yield SSEMessage.create(
                                        content=content,
                                        event_type="openrouter"
                                    )
                            except json.JSONDecodeError:
                                logger.error(f"OpenRouter API JSON解析失败，原始数据为: {line}")
                                continue
                            except KeyError as e:
                                logger.error(f"OpenRouter API 返回数据结构异常: {str(e)}, 数据: {data}")
                                continue
                    
        except Exception as e:
            logger.error(f"OpenRouter Chat API 调用失败: {str(e)}", exc_info=True)
            raise 
