from pydantic import BaseModel, Field
from typing import Optional

class CozeArticleContent(BaseModel):
    key0_background: str = Field(..., description="文章背景信息")
    key1_people: str = Field(..., description="人物介绍")
    key2_why: str = Field(..., description="为什么要读")
    key3_core: str = Field(..., description="核心观点")
    key4_word: str = Field(..., description="名词解释")
    key5_summary: str = Field(..., description="整体总结")
    key6_part_title: str = Field(..., description="分段提纲")
    key7_part_detail: str = Field(default="", description="分段详述")
    key8_qa: str = Field(..., description="QA环节")
    key9_golden: str = Field(..., description="金句")
    key10_exclude: str = Field(..., description="未总结内容")
    key11_map: str = Field(..., description="结构图")
    key19_Takeaways: str = Field(..., description="要点总结")
    key17_xmind: str = Field(..., description="思维导图")
    key18_EasterEgg: str = Field(..., description="彩蛋")
    key20_case: str = Field(..., description="典型案例")
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