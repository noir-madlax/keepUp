from typing import Optional
from pydantic import BaseModel
from typing import List

class FetchRequest(BaseModel):
    id: int
    url: str
    languages: List[str] = ['zh']  # 默认中文,可选 ['zh', 'en']

class ParseRequest(BaseModel):
    id: int
    url: str
    content: Optional[str] = None 
    chapters: Optional[str] = None 