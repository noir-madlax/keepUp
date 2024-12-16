from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class LogCreate(BaseModel):
    """创建日志记录的模型"""
    request_id: int
    level: str
    message: str
    step: str
    error_trace: Optional[str] = None
    metadata: Optional[dict] = None

class Log(LogCreate):
    """完整的日志记录模型"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 