from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import Optional
from uuid import UUID
from app.services.chat import ChatService
from app.models.chat import ChatResponse, PromptType

router = APIRouter()

@router.post("/chat/{session_id}/stream")
async def process_chat_stream(
    session_id: UUID,
    prompt_type: Optional[PromptType] = Query(
        default=PromptType.BASE,
        description="选择系统提示类型：base(默认)、elaborate、explain、origin"
    )
):
    """处理流式聊天请求"""
    try:
        chat_service = ChatService()
        return StreamingResponse(
            chat_service.process_chat_stream(session_id, prompt_type),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 