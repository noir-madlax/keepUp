from typing import Optional
from pydantic import BaseModel
from typing import List

class FetchRequest(BaseModel):
    id: Optional[int] = None
    url: str
    summary_languages: List[str] = ['zh']  # 默认中文,可选 ['zh', 'en']
    subtitle_languages: List[str] = ['zh']  # 默认中文,可选 ['zh', 'en']
    detailed_languages: List[str] = ['zh']  # 默认中文,可选 ['zh', 'en']

class ParseRequest(BaseModel):
    id: int
    url: str
    content: Optional[str] = None 
    chapters: Optional[str] = None 