from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PromptModel(BaseModel):
    id: int
    type: str
    name: str
    content: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None 