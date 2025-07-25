from supabase import create_client, Client
from app.config import settings
from app.utils.logger import logger
from app.models.coze import ArticleCreate
import json
from typing import Optional, Dict

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
        # 检查标题是否为空
        if not article_data.title or not article_data.title.strip():
            logger.warning("文章标题为空，取消创建")
            raise ValueError("文章标题不能为空")
        
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
                "sort_order": section.get("sort_order", idx),
                "language": section["language"]
            }
            for idx, section in enumerate(sections)
        ]
        result = client.table("keep_article_sections").insert(sections_data).execute()
        logger.info(f"文章小节创建成功: {len(sections)} 个小节")
        return result.data
    
    @classmethod
    async def update_content(cls, request_id: int, content: str):
        """更新请求"""
        client = cls.get_client()
        result = client.table("keep_article_requests").update({
            "content": content
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
                "icon": author_data.get("icon", None)  # 默认无头像
            }).execute()
            
            logger.info(f"作者创建成功: {author_data['name']}")
            return result.data[0]
            
        except Exception as e:
            logger.error(f"创建作者失败: {str(e)}", exc_info=True)
            raise
    
    @classmethod
    async def update_author(cls, author_id: int, author_data: dict):
        """更新作者信息

        Args:
            author_id: 作者ID
            author_data: 作者数据,包含以下字段:
                - name: 作者名称
                - icon: 作者头像URL
                
        Returns:
            更新后的作者数据记录
        """
        client = cls.get_client()
        update_data = {
            "name": author_data["name"],
            "icon": author_data.get("icon")
        }
        result = client.table("keep_authors").update(update_data).eq("id", author_id).execute()
        logger.info(f"作者更新成功: ID={author_id}, name={update_data['name']}")
        return result.data[0]
    
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
    
    @classmethod
    async def delete_article_section(
        cls,
        article_id: int,
        section_type: str,
        language: str
    ) -> None:
        """除指定文章的特定类型和语言的小节
        
        Args:
            article_id: 文章ID
            section_type: 小节类型
            language: 语言类型
        """
        client = cls.get_client()
        result = client.table("keep_article_sections").delete().match({
            "article_id": article_id,
            "section_type": section_type,
            "language": language
        }).execute()
        
        logger.info(f"删除小节成功: article_id={article_id}, type={section_type}, language={language}")
        return result
    
    @classmethod
    async def get_request_id_by_article_id(cls, article_id: int) -> int:
        """通过文章ID获取对应的请求ID
        
        直接通过 article_id 字段查询 article_requests 表,
        如果有多条记录则返回第一条。
        
        Args:
            article_id: 文章ID
            
        Returns:
            int: 请求ID
            
        Raises:
            ValueError: 当找不到对应的请求记录时
        """
        try:
            logger.info(f"开始查找文章对应的请求ID: article_id={article_id}")
            
            client = cls.get_client()
            request_result = client.table("keep_article_requests")\
                .select("id")\
                .eq("article_id", article_id)\
                .execute()
            
            if not request_result.data:
                raise ValueError(f"未找到对应的请求记录: article_id={article_id}")
            
            # 取第一条记录的ID
            request_id = request_result.data[0].get("id")
            logger.info(f"找到对应的请求ID: article_id={article_id}, request_id={request_id}")
            
            return request_id
            
        except Exception as e:
            logger.error(f"查找请求ID失败: {str(e)}", exc_info=True)
            raise
    
    @classmethod
    async def update_polished_content(
        cls,
        request_id: int,
        polished_content: dict,
        language: str
    ) -> None:
        """更新请求的润色内容
        
        Args:
            request_id: 请求ID
            polished_content: Coze返回的润色结果
            language: 语言类型
        """
        try:
            client = cls.get_client()
            
            # 将结果转换为JSON字符串
            polished_content_json = json.dumps(polished_content, ensure_ascii=False)
            
            # 根据语言类型设置字段名
            field_name = f"polished_content_{language}"
            
            # 更新数据
            result = client.table('keep_article_requests').update({
                field_name: polished_content_json
            }).eq('id', request_id).execute()
            
            if not result.data:
                raise Exception(f"未找到 ID 为 {request_id} 的请求记录")
            
            logger.info(f"润色内容更新成功: ID={request_id}, language={language}")
            
        except Exception as e:
            logger.error(f"更新润色内容失败: {str(e)}", exc_info=True)
            raise
    
    @classmethod
    async def update_detailed_content(
        cls,
        request_id: int,
        detailed_content: dict,
        language: str
    ) -> None:
        """更新请求的分段详述内容
        
        Args:
            request_id: 请求ID
            detailed_content: Coze返回的分段详述结果
            language: 语言类型
        """
        try:
            client = cls.get_client()
            
            # 将结果转换为JSON字符串
            detailed_content_json = json.dumps(detailed_content, ensure_ascii=False)
            
            # 根据语言类型设置字段名
            field_name = f"detailed_content_{language}"
            
            # 更新数据
            result = client.table('keep_article_requests').update({
                field_name: detailed_content_json
            }).eq('id', request_id).execute()
            
            if not result.data:
                raise Exception(f"未找到 ID 为 {request_id} 的请求记录")
            
            logger.info(f"分段详述内容更新成功: ID={request_id}, language={language}")
            
        except Exception as e:
            logger.error(f"更新分段详述内容失败: {str(e)}", exc_info=True)
            raise
    
    @classmethod
    async def update_chapters(cls, request_id: int, chapters: str) -> None:
        """更新请求的章节信息
        
        Args:
            request_id: 请求ID
            chapters: 章节信息
        """
        try:
            client = cls.get_client()
            
            result = client.table('keep_article_requests').update({
                'chapters': chapters
            }).eq('id', request_id).execute()
            
            if not result.data:
                raise Exception(f"未找到 ID 为 {request_id} 的请求记录")
            
            logger.info(f"章节信息更新成功: ID={request_id}, 长度: {len(chapters) if chapters else 0}")
            
        except Exception as e:
            logger.error(f"更新章节信息失败: {str(e)}", exc_info=True)
            raise
    
    @classmethod
    async def get_article_section_by_type(
        cls,
        article_id: int,
        section_type: str
    ) -> list:
        """获取文章指定类型的所有小节
        
        Args:
            article_id: 文章ID
            section_type: 小节类型
            
        Returns:
            list: 小节信息列表，如果未找到则返回空列表
        """
        try:
            client = cls.get_client()
            
            # 查询指定类型的所有小节，按创建时间排序
            result = client.table("keep_article_sections").select("*").match({
                "article_id": article_id,
                "section_type": section_type
            }).order("created_at").execute()
            
            if result.data:
                logger.info(f"找到文章小节: article_id={article_id}, type={section_type}, count={len(result.data)}")
                return result.data
            
            logger.info(f"未找到文章小节: article_id={article_id}, type={section_type}")
            return []
            
        except Exception as e:
            logger.error(f"获取文章小节失败: {str(e)}", exc_info=True)
            return []
    
    @classmethod
    async def get_article_request(cls, request_id: int) -> dict:
        """获取文章请求记录
        
        Args:
            request_id: 请求ID
            
        Returns:
            dict: 请求记录
        """
        try:
            client = cls.get_client()
            response = client.table('keep_article_requests').select('*').eq('id', request_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"获取文章请求记录失败: {str(e)}")
            raise
    
    @classmethod
    async def update_request_url(cls, request_id: int, url: str) -> None:
        """更新文章请求的URL
        
        Args:
            request_id: 请求ID
            url: 新的URL地址
        """
        try:
            client = cls.get_client()
            
            result = client.table('keep_article_requests').update({
                'url': url
            }).eq('id', request_id).execute()
            
            if not result.data:
                raise Exception(f"未找到 ID 为 {request_id} 的请求记录")
            
            logger.info(f"URL更新成功: ID={request_id}, URL={url}")
            
        except Exception as e:
            logger.error(f"更新URL失败: {str(e)}", exc_info=True)
            raise
    
    @classmethod
    async def update_request_platform(
        cls,
        request_id: int,
        platform: str,
        parsed_url: str,
        original_url: str
    ) -> None:
        """更新请求的平台信息
        
        Args:
            request_id: 请求ID
            platform: 平台类型(youtube/apple/spotify)
            parsed_url: 解析后的YouTube URL
            original_url: 原始URL
        """
        try:
            client = cls.get_client()
            
            result = client.table('keep_article_requests').update({
                'platform': platform,
                'url': parsed_url,
                'original_url': original_url
            }).eq('id', request_id).execute()
            
            if not result.data:
                raise Exception(f"未找到 ID 为 {request_id} 的请求记录")
            
            logger.info(f"平台信息更新成功: ID={request_id}, Platform={platform}")
            
        except Exception as e:
            logger.error(f"更新平台信息失败: {str(e)}", exc_info=True)
            raise
    
    @classmethod
    async def check_url_exists(cls, url: str) -> bool:
        """检查URL是否已存在
        
        Args:
            url: 要检查的URL
            
        Returns:
            bool: True 如果URL已存在，False 如果不存在
        """
        try:
            client = cls.get_client()
            
            # 使用 Supabase Filter 语法
            result = client.table('keep_article_requests').select('id').filter(
                'original_url', 'eq', url
            ).execute()
            
            # 如果没找到原始URL，再检查解析后的URL
            if not result.data:
                result = client.table('keep_article_requests').select('id').filter(
                    'url', 'eq', url
                ).execute()
            
            exists = bool(result.data)
            if exists:
                logger.info(f"URL已存在: {url}")
            
            return exists
            
        except Exception as e:
            logger.error(f"检查URL是否存在时失败: {str(e)}", exc_info=True)
            return False
    
    @classmethod
    async def create_article_request(cls, request_data: dict) -> dict:
        """创建文章请求记录
        
        Args:
            request_data: 请求数据
            
        Returns:
            dict: 创建的请求记录
        """
        try:
            client = cls.get_client()
            result = client.table('keep_article_requests').insert(request_data).execute()
            
            if not result.data:
                raise Exception("创建请求记录失败")
            
            logger.info(f"创建请求记录成功: ID={result.data[0]['id']}")
            return result.data[0]
            
        except Exception as e:
            logger.error(f"创建请求记录失败: {str(e)}", exc_info=True)
            raise
    
    @classmethod
    async def get_article_by_request_id(cls, request_id: int) -> Optional[Dict]:
        """通过请求ID获取文章信息
        
        Args:
            request_id: 请求ID
            
        Returns:
            Optional[Dict]: 文章信息或None
        """
        try:
            # 1. 获取请求记录以获取 article_id
            request = await cls.get_article_request(request_id)
            if not request or not request.get('article_id'):
                logger.warning(f"找不到请求记录或请求记录缺少文章ID: request_id={request_id}")
                return None
            
            # 2. 通过 article_id 直接查询文章
            client = cls.get_client()
            response = client.table('keep_articles')\
                .select('*')\
                .eq('id', request.get('article_id'))\
                .single()\
                .execute()
            
            if response.data:
                return response.data
            
            logger.warning(f"找不到对应的文章: request_id={request_id}, article_id={request.get('article_id')}")
            return None
            
        except Exception as e:
            logger.error(f"获取文章信息失败: request_id={request_id}, error={str(e)}")
            return None
    
    @classmethod
    async def get_article_by_id(cls, article_id: int) -> Optional[Dict]:
        """通过文章ID获取文章信息
        
        Args:
            article_id: 文章ID
            
        Returns:
            Optional[Dict]: 文章信息或None
        """
        try:
            client = cls.get_client()
            response = client.table('keep_articles')\
                .select('*')\
                .eq('id', article_id)\
                .single()\
                .execute()
            
            if response.data:
                return response.data
            
            logger.warning(f"找不到对应的文章: article_id={article_id}")
            return None
            
        except Exception as e:
            logger.error(f"获取文章信息失败: article_id={article_id}, error={str(e)}")
            return None
    
    @classmethod
    async def update_article_visibility(cls, article_id: int, is_visible: bool) -> None:
        """更新文章可见性状态
        
        Args:
            article_id: 文章ID
            is_visible: 是否可见
        """
        try:
            client = cls.get_client()
            
            result = client.table('keep_articles').update({
                'is_visible': is_visible
            }).eq('id', article_id).execute()
            
            if not result.data:
                raise Exception(f"未找到 ID 为 {article_id} 的文章")
            
            logger.info(f"文章可见性更新成功: ID={article_id}, is_visible={is_visible}")
            
        except Exception as e:
            logger.error(f"更新文章可见性失败: {str(e)}", exc_info=True)
            raise
    
    @classmethod
    async def update_article_id(cls, request_id: int, article_id: int) -> None:
        """更新请求记录的文章ID
        
        Args:
            request_id: 请求ID
            article_id: 文章ID
        """
        try:
            client = cls.get_client()
            
            result = client.table('keep_article_requests').update({
                'article_id': article_id
            }).eq('id', request_id).execute()
            
            if not result.data:
                raise Exception(f"未找到 ID 为 {request_id} 的请求记录")
            
            logger.info(f"请求记录文章ID更新成功: request_id={request_id}, article_id={article_id}")
            
        except Exception as e:
            logger.error(f"更新请求记录文章ID失败: {str(e)}", exc_info=True)
            raise