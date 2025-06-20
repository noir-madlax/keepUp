from typing import Optional, Dict
from .base import ContentFetcher, VideoInfo, AuthorInfo
from app.models.article import ArticleCreate
from app.utils.logger import logger
from app.models.request import FetchRequest

class FileFetcher(ContentFetcher):
    """文件内容获取器"""
    
    def can_handle(self, url: str) -> bool:
        """检查是否是文件类型"""
        return url.startswith('file://')
        
    async def fetch(self, url: str, request: Optional[FetchRequest] = None) -> Optional[str]:
        """获取文件内容"""
        if request and request.content:
            logger.info(f"从请求中获取文件内容: {len(request.content)} 字符")
            return request.content
        return None
        
    async def get_video_info(self, url: str) -> Optional[VideoInfo]:
        """获取文件信息"""
        try:
            # 从文件名中提取标题
            filename = url.replace('file://', '')
            
            # 创建文章数据
            article = ArticleCreate(
                title=filename,
                content="",  # 内容会在后续步骤中填充
                channel="file",
                original_link=filename
            )
            
            # 创建作者信息
            author = {
                "name": "File Upload",
                "platform": "file",
                "icon": "/images/icons/file.svg"
            }
            
            return VideoInfo(
                title=filename,
                description="",  # 文件没有描述
                author=author,
                article=article
            )
            
        except Exception as e:
            logger.error(f"获取文件信息失败: {str(e)}")
            return None
            
    async def get_chapters(self, url: str) -> Optional[str]:
        """获取文件章节信息 - 文件暂不支持章节"""
        return None 

    async def get_author_info(self, url: str) -> Optional[AuthorInfo]:
        """获取文件作者信息"""
        pass 