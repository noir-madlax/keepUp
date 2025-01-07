from typing import List, Optional
from uuid import UUID
from app.models.chat import ChatMessage, ChatSession
from app.repositories.supabase import SupabaseService

class ChatRepository:
    def __init__(self):
        self.client = SupabaseService.get_client()
        
    async def get_session(self, session_id: UUID) -> Optional[ChatSession]:
        """获取会话信息"""
        result = self.client.table("keep_chat_sessions").select("*").eq("id", session_id).execute()
        
        if result.data:
            return ChatSession(**result.data[0])
        return None
        
    async def get_messages(self, session_id: UUID) -> List[ChatMessage]:
        """获取会话的历史消息"""
        result = self.client.table("keep_chat_messages")\
            .select("*")\
            .eq("session_id", session_id)\
            .order("created_at")\
            .execute()
            
        return [ChatMessage(**msg) for msg in result.data]
        
    async def save_message(self, session_id: UUID, role: str, content: str) -> None:
        """保存新消息"""
        self.client.table("keep_chat_messages").insert({
            "session_id": str(session_id),
            "role": role,
            "content": content
        }).execute() 