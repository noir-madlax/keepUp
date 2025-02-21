from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AuthorInfo(BaseModel):
    """作者信息模型"""
    name: str
    icon: Optional[str] = None
    platform: str 