from supabase import create_client, Client
from app.config import settings
from app.utils.logger import logger
from app.models.coze import ArticleCreate

class SupabaseService:
    _client: Client = None
    
    @classmethod
    def get_client(cls) -> Client:
        if cls._client is None:
            cls._client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_ROLE_KEY
            )
        return cls._client
    
    @classmethod
    async def update_status(cls, request_id: int, status: str, error_message: str = None):
        client = cls.get_client()
        data = {"status": status}
        if error_message:
            data["error_message"] = error_message
            
        result = client.table("keep_article_requests").update(data).eq("id", request_id).execute()
        logger.info(f"状态更新成功: ID={request_id}, status={status}")
        return result
    
    @classmethod
    async def update_result(cls, request_id: int, status: str):
        client = cls.get_client()
        result = client.table("keep_article_requests").update({
            "status": status
        }).eq("id", request_id).execute()
        logger.info(f"结果更新成功: ID={request_id}")
        return result 
    
    @classmethod
    async def create_article(cls, article_data: 'ArticleCreate'):
        """创建新文章"""
        client = cls.get_client()
        result = client.table("keep_articles").insert(article_data.dict()).execute()
        logger.info(f"文章创建成功")
        return result.data[0]
    
    @classmethod
    async def create_article_sections(cls, article_id: int, sections: list[dict]):
        """创建文章小节"""
        client = cls.get_client()
        sections_data = [
            {
                "article_id": article_id,
                "section_type": section["section_type"],
                "content": section["content"],
                "sort_order": idx
            }
            for idx, section in enumerate(sections)
        ]
        result = client.table("keep_article_sections").insert(sections_data).execute()
        logger.info(f"文章小节创建成功: {len(sections)} 个小节")
        return result.data