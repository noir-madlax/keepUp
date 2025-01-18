from fastapi import APIRouter, HTTPException
from ..repositories.article_views import ArticleViewsRepository
from pydantic import BaseModel

router = APIRouter()

class ArticleViewModel(BaseModel):
    user_id: str
    article_id: int

@router.post("/article-views/record")
async def record_article_view(view: ArticleViewModel):
    """记录文章访问"""
    try:
        await ArticleViewsRepository.record_article_view(
            user_id=view.user_id,
            article_id=view.article_id
        )
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))