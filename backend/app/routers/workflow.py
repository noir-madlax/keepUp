from fastapi import APIRouter, HTTPException
from app.models.request import FetchRequest, ParseRequest
from app.services.content_fetcher.service import ContentFetcherService
from app.services.supabase import SupabaseService
from app.utils.logger import logger
from app.routers.parse import call_coze_and_parse, process_coze_result
import asyncio

router = APIRouter()

@router.post("/workflow/process")
async def process_workflow(request: FetchRequest):
    """完整的处理流程"""
    try:
        logger.info(f"开始完整处理流程: ID={request.id}, URL={request.url}")
        
        # 1. 更新状态为处理中
        await SupabaseService.update_status(request.id, "processing")
        
        # 2. 获取视频基础信息
        service = ContentFetcherService()
        video_info = await service.get_video_info(request.url)
        
        if not video_info:
            raise HTTPException(status_code=400, detail="无法获取视频信息")
            
        # 3. 获取视频章节信息
        chapters = await service.get_chapters(request.url)
        logger.info(f"获取到章节信息: {len(chapters) if chapters else 0} 个章节")
        
        # 4. 处理作者信息
        author = await SupabaseService.get_author_by_name(video_info.author["name"])
        if not author:
            # 创建新作者
            author = await SupabaseService.create_author(video_info.author)
            
        # 5. 创建文章基础信息
        article_data = video_info.article
        article_data.author_id = author["id"]
        article = await SupabaseService.create_article(article_data)
        
        # 6. 获取视频字幕
        content = await service.fetch_content(request.url)
        if not content:
            raise HTTPException(status_code=400, detail="无法获取字幕内容")
        
        # 7. 保存字幕内容
        await SupabaseService.update_content(request.id, content)
        
        # 等待确保数据已保存
        await asyncio.sleep(1)
        
        # 8. 调用解析服务
        parse_request = ParseRequest(id=request.id, url=request.url, content=content, chapters=chapters)
        coze_response = await call_coze_and_parse(parse_request.url, parse_request.content, parse_request.chapters)
        
        # 9. 处理解析结果
        await process_coze_result(coze_response, request.id, request.url,article)
        
        return {
            "success": True,
            "message": "处理完成",
            "steps": [
                "获取视频信息成功",
                "获取章节信息成功",
                "处理作者信息成功",
                "创建文章成功",
                "获取字幕成功",
                "解析内容成功",
                "保存结果成功"
            ]
        }
        
    except Exception as e:
        logger.error(f"工作流处理失败: {str(e)}", exc_info=True)
        await SupabaseService.update_status(
            request.id, 
            "failed", 
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e)) 