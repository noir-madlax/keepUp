from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

class PromptType(Enum):
    BASE = "base"
    ELABORATE = "elaborate"
    EXPLAIN = "explain"
    ORIGIN = "origin"

class ChatMessage(BaseModel):
    role: str
    content: str
    
class ChatSession(BaseModel):
    id: UUID
    article_id: int
    mark_type: str
    mark_content: str
    section_type: Optional[str]
    context: Optional[dict]

class ChatResponse(BaseModel):
    content: str 