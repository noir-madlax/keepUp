from typing import List
import json
from uuid import UUID
from app.services.deepseek import DeepseekService
from app.repositories.chat import ChatRepository
from app.repositories.supabase import SupabaseService
from app.utils.logger import logger
from app.models.chat import ChatMessage, ChatSession

class ChatService:
    def __init__(self):
        self.chat_repository = ChatRepository()
        self.deepseek_service = DeepseekService()
        
    async def process_chat(self, session_id: UUID) -> str:
        """处理聊天请求的完整流程"""
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
            
            # 5. 调用 Deepseek API
            response = await self.deepseek_service.chat(context)
            
            # 6. 保存响应
            await self.chat_repository.save_message(
                session_id=session_id,
                role="assistant",
                content=response
            )
            
            return response
            
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
        # 构建基础提示信息
        base_prompt = f"""基于以下文章内容回答问题。
        
        文章内容:
        {article_content}

        当前选中内容:
        {session.mark_content}

        """
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