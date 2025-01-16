from pydantic import BaseModel, Field
from typing import Optional

class CozeArticleContent(BaseModel):
    key0_background:  Optional[str] = Field(None, description="文章背景信息")
    key1_people:  Optional[str] = Field(None, description="人物介绍")
    key2_why:  str = Field(None, description="为什么要读")
    key3_core:  Optional[str] = Field(None, description="核心观点")
    key4_word:  Optional[str] = Field(None, description="名词解释")
    key5_summary:  Optional[str] = Field(None, description="总结")
    key6_part_title:  Optional[str] = Field(None, description="分段提纲")
    key7_part_detail:  Optional[str] = Field(None, description="分段详述")
    key8_qa:  Optional[str] = Field(None, description="QA环节")
    key9_golden:  Optional[str] = Field(None, description="金句")
    key10_exclude:  Optional[str] = Field(None, description="未总结内容")
    key11_map:  Optional[str] = Field(None, description="结构图")
    key19_Takeaways:  Optional[str] = Field(None, description="要点总结")
    key17_xmind:  Optional[str] = Field(None, description="思维导图")
    key18_EasterEgg:  Optional[str] = Field(None, description="彩蛋")
    key20_case:  Optional[str] = Field(None, description="典型案例")
    video_author_name: Optional[str] = None
    video_date: Optional[str] = None
    video_link: Optional[str] = None
    video_original_content: Optional[str] = None

class CozeResponse(BaseModel):
    code: int
    cost: str
    data: str  # JSON string
    debug_url: str
    msg: str
    token: int

class ArticleCreate(BaseModel):
    title: str
    content: str
    author_id: int = 1  # 默认作者ID
    channel: str = "YouTube"  # 默认渠道
    tags: list[str] = ["视频"]  # 默认标签
    original_link: str 