from typing import Optional
from pydantic import BaseModel
from typing import List

class FetchRequest(BaseModel):
    id: Optional[int] = None
    original_url: Optional[str] = None  # 原始URL
    parsed_url: Optional[str] = None # 解析后的URL
    user_id: Optional[str] = None  # 添加用户ID字段
    summary_languages: List[str] = ['zh']  # 默认中文,可选 ['zh', 'en']
    subtitle_languages: List[str] = ['zh']  # 默认中文,可选 ['zh', 'en']
    detailed_languages: List[str] = ['zh']  # 默认中文,可选 ['zh', 'en']
    platform: Optional[str] = None # 平台
    content: Optional[str] = None # 文本
    article_id: Optional[int] = None

class ParseRequest(BaseModel):
    id: int
    url: str
    content: Optional[str] = None 
    chapters: Optional[str] = None 

class AppendRequest(BaseModel):
    """追加内容请求模型"""
    article_id: int
    summary_languages: List[str] = []
    subtitle_languages: List[str] = []
    detailed_languages: List[str] = [] 