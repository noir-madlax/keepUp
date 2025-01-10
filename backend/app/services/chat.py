from typing import List, AsyncGenerator
import json
from uuid import UUID
from app.services.deepseek import DeepseekService
from app.repositories.chat import ChatRepository
from app.repositories.supabase import SupabaseService
from app.utils.logger import logger
from app.models.chat import ChatMessage, ChatSession
from app.templates.prompts import BASE_CHAT_PROMPT, PROMPT_MAPPING

class ChatService:
    def __init__(self):
        self.chat_repository = ChatRepository()
        self.deepseek_service = DeepseekService()
        
    @staticmethod
    def _extract_content_from_sse_response(response_chunks: List[str]) -> str:
        """从 SSE 响应中提取完整的 content"""
        try:
            
            content_parts = []
            for i, chunk in enumerate(response_chunks):
                try:
                    if chunk.startswith('data: '):
                        data_str = chunk[6:]
                        if data_str == '[DONE]':
                            continue
                        data = json.loads(data_str)
                        if content := data.get('content'):
                            content_parts.append(content)
                except Exception as e:
                    logger.warning(f"处理响应块失败: {str(e)}, chunk: {chunk}")
                    continue
                    
            final_content = ''.join(content_parts)
            logger.info(f"最终拼接的内容: {final_content}")  # 打印最终结果
            return final_content
            
        except Exception as e:
            logger.error(f"提取 content 失败: {str(e)}")
            return ''
            
    async def process_chat_stream(self, session_id: UUID) -> AsyncGenerator[str, None]:
        """处理流式聊天请求"""
        try:
            # 1. 获取会话信息
            session = await self.chat_repository.get_session(session_id)
            if not session:
                raise ValueError(f"Session not found: {session_id}")
                
            # 2. 获取历史消息
            messages = await self.chat_repository.get_messages(session_id)
            
            # 3. 获取文章内容
            article_content = await self._get_article_content(session.article_id)
            if not article_content:
                raise ValueError(f"Article content not found: article_id={session.article_id}")
            
            # 4. 构建上下文
            context = self._build_context(
                session=session,
                messages=messages,
                article_content=article_content
            )
            
            # 5. 流式调用 Deepseek API
            response_chunks = []
            async for chunk in self.deepseek_service.chat_stream(context):
                response_chunks.append(chunk)
                yield chunk
            
            # 6. 提取并保存完整响应
            complete_content = self._extract_content_from_sse_response(response_chunks)
            if complete_content:  # 只在有内容时保存
                await self.chat_repository.save_message(
                    session_id=session_id,
                    role="assistant",
                    content=complete_content
                )
            
        except Exception as e:
            logger.error(f"处理聊天请求失败: {str(e)}", exc_info=True)
            raise
            
    async def _get_article_content(self, article_id: int) -> str:
        """获取文章内容
        
        Args:
            article_id: 文章ID
            
        Returns:
            str: 文章内容
            
        Raises:
            ValueError: 当找不到文章内容时
        """
        try:
            # 1. 获取请求ID
            request_id = await SupabaseService.get_request_id_by_article_id(article_id)
            if not request_id:
                raise ValueError(f"未找到文章对应的请求: article_id={article_id}")
                
            # 2. 获取文章请求信息
            article_request = await SupabaseService.get_article_request(request_id)
            if not article_request:
                raise ValueError(f"未找到请求信息: request_id={request_id}")
                
            # 3. 返回文章内容
            content = article_request.get("content")
            if not content:
                raise ValueError(f"文章内容为空: request_id={request_id}")
                
            return content
            
        except Exception as e:
            logger.error(f"获取文章内容失败: {str(e)}", exc_info=True)
            raise
            
    def _build_context(self, session: ChatSession, messages: List[ChatMessage], article_content: str) -> dict:
        """构建发送给 Deepseek 的上下文"""
        # 根据 mark_type 选择合适的提示模板
        prompt_template = PROMPT_MAPPING.get(session.mark_type, BASE_CHAT_PROMPT)
        
        # 构建提示信息
        base_prompt = prompt_template.format(
            article_content=article_content,
            mark_content=session.mark_content
        )
        
        # 添加历史消息
        history = []
        for msg in messages[-5:]:  # 只保留最近5轮对话
            history.append({
                "role": msg.role,
                "content": msg.content
            })
            
        return {
            "prompt": base_prompt,
            "history": history,
            "section_type": session.section_type,
            "mark_type": session.mark_type
        } 