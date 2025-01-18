from app.utils.logger import logger
from .supabase import SupabaseService

class ArticleViewsRepository:
    @classmethod
    async def create_article_view(cls, user_id: str, article_id: int, is_author: bool = False):
        """
        创建文章浏览记录
        
        Args:
            user_id: 用户ID
            article_id: 文章ID
            is_author: 是否是作者（默认False）
        """
        try:
            client = SupabaseService.get_client()
            
            data = {
                "user_id": user_id,
                "article_id": article_id,
                "is_author": is_author,
            }
            
            result = client.table("keep_article_views").upsert(
                data,
                on_conflict="user_id,article_id"  # 如果记录已存在则更新
            ).execute()
            
            logger.info(f"创建文章浏览记录成功: user_id={user_id}, article_id={article_id}, is_author={is_author}")
            return result.data
            
        except Exception as e:
            logger.error(f"创建文章浏览记录失败: {str(e)}", exc_info=True)
            raise 

    @classmethod
    async def record_article_view(cls, user_id: str, article_id: int):
        """
        记录文章访问，如果记录存在则更新访问次数和最后访问时间
        
        Args:
            user_id: 用户ID
            article_id: 文章ID
        """
        try:
            client = SupabaseService.get_client()
            
            # 先查询是否存在记录
            existing = client.table("keep_article_views")\
                .select("*")\
                .eq("user_id", user_id)\
                .eq("article_id", article_id)\
                .execute()
                
            if existing.data:
                # 如果存在记录则更新
                data = {
                    "last_viewed_at": "now()",
                    "view_count": existing.data[0]["view_count"] + 1
                }
                result = client.table("keep_article_views")\
                    .update(data)\
                    .eq("user_id", user_id)\
                    .eq("article_id", article_id)\
                    .execute()
            else:
                # 如果不存在则创建新记录
                data = {
                    "user_id": user_id,
                    "article_id": article_id,
                    "last_viewed_at": "now()",
                    "view_count": 1
                }
                result = client.table("keep_article_views")\
                    .insert(data)\
                    .execute()
            
            logger.info(f"更新文章访问记录成功: user_id={user_id}, article_id={article_id}")
            return result.data
            
        except Exception as e:
            logger.error(f"更新文章访问记录失败: {str(e)}", exc_info=True)
            raise