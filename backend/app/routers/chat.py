from fastapi import APIRouter, HTTPException
from typing import Optional
from uuid import UUID
from app.services.chat import ChatService
from app.models.chat import ChatResponse

router = APIRouter()

@router.post("/chat/{session_id}", response_model=ChatResponse)
async def process_chat(session_id: UUID):
    """处理聊天请求
    
    Args:
        session_id: 会话ID
        
    Returns:
        ChatResponse: 包含AI响应的结果
    """
    try:
        chat_service = ChatService()
        response = await chat_service.process_chat(session_id)
        return ChatResponse(content=response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 