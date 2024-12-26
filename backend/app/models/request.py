from typing import Optional
from pydantic import BaseModel
from typing import List

class FetchRequest(BaseModel):
    id: Optional[int] = None
    original_url: Optional[str] = None  # 原始URL
    user_id: Optional[str] = None  # 添加用户ID字段
    summary_languages: List[str] = ['zh']  # 默认中文,可选 ['zh', 'en']
    subtitle_languages: List[str] = ['zh']  # 默认中文,可选 ['zh', 'en']
    detailed_languages: List[str] = ['zh']  # 默认中文,可选 ['zh', 'en']
    platform: Optional[str] = None # 平台
    parsed_url: Optional[str] = None # 解析后的URL

class ParseRequest(BaseModel):
    id: int
    url: str
    content: Optional[str] = None 
    chapters: Optional[str] = None 