from supabase import create_client, Client
from app.config import settings
from app.utils.logger import logger
from app.models.coze import ArticleCreate
import json

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
    
    @classmethod
    async def update_content(cls, request_id: int, content: str):
        """更新请求内容"""
        client = cls.get_client()
        result = client.table("keep_article_requests").update({
            "content": content,
            "status": "processed"
        }).eq("id", request_id).execute()
        logger.info(f"内容更新成功: ID={request_id}")
        return result
    
    @classmethod
    async def update_parsed_content(cls, request_id: int, parsed_content: dict) -> None:
        """更新请求的解析内容"""
        try:
            client = cls.get_client()
            parsed_content_json = json.dumps(parsed_content, ensure_ascii=False)
            
            result = client.table('keep_article_requests').update({
                'parsed_content': parsed_content_json
            }).eq('id', request_id).execute()
            
            if not result.data:
                raise Exception(f"未找到 ID 为 {request_id} 的请求记录")
            
            logger.info(f"解析内容更新成功: ID={request_id}")
            
        except Exception as e:
            logger.error(f"更新解析内容失败: {str(e)}", exc_info=True)
            raise
    
    @classmethod
    async def create_author(cls, author_data: dict):
        """创建新作者"""
        try:
            client = cls.get_client()
            result = client.table("keep_authors").insert({
                "name": author_data["name"],
                # "platform": author_data.get("platform", "YouTube"),  # 添加平台信息
                "icon": None  # 默认无头像
            }).execute()
            
            logger.info(f"作者创建成功: {author_data['name']}")
            return result.data[0]
            
        except Exception as e:
            logger.error(f"创建作者失败: {str(e)}", exc_info=True)
            raise
    
    @classmethod
    async def get_author_by_name(cls, name: str):
        """根据作者名称获取作者信息"""
        try:
            client = cls.get_client()
            result = client.table("keep_authors").select("*").eq("name", name).execute()
            
            if result.data:
                logger.info(f"找到作者: {name}")
                return result.data[0]
            
            logger.info(f"未找到作者: {name}")
            return None
            
        except Exception as e:
            logger.error(f"获取作者信息失败: {str(e)}", exc_info=True)
            return None