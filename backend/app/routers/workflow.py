from fastapi import APIRouter, HTTPException
from app.models.request import FetchRequest, ParseRequest
from app.services.content_fetcher.service import ContentFetcherService
from app.services.supabase import SupabaseService
from app.utils.logger import logger
from app.routers.parse import call_coze_and_parse, process_coze_result
from app.config import settings
import asyncio

router = APIRouter()

async def process_multilingual_content(request_id: int, url: str, content: str, chapters: str, article, languages: list[str]) -> list[str]:
    """处理多语言内容解析
    
    Args:
        request_id: 请求ID
        url: 视频URL
        content: 视频内容
        chapters: 章节信息
        article: 文章信息
        languages: 需要处理的语言列表
        
    Returns:
        list[str]: 处理结果信息列表
    """
    results = []
    logger.info(f"开始多语言内容处理 - 请求ID: {request_id}, 语言列表: {languages}")
    
    for lang in languages:
        
        workflow_id = (
            settings.COZE_WORKFLOW_ID_ZH if lang == 'zh' 
            else settings.COZE_WORKFLOW_ID_EN
        )
        logger.info(f"使用工作流 ID: {workflow_id} 处理 {lang} 语言")
        
        try:
            # 调用对应语言的工作流
            parse_request = ParseRequest(
                id=request_id, 
                url=url, 
                content=content, 
                chapters=chapters
            )
            logger.info(f"调用 Coze API 解析 {lang} 内容 - 请求ID: {request_id}")
            
            coze_response = await call_coze_and_parse(
                parse_request.url, 
                parse_request.content, 
                parse_request.chapters,
                workflow_id
            )
            
            # 处理解析结果,添加语言标识
            logger.info(f"开始保存 {lang} 解析结果 - 请求ID: {request_id}")
            await process_coze_result(
                coze_response, 
                request_id, 
                url,
                article,
                lang
            )
            
            results.append(f"{lang} 内容处理完成")
            
        except Exception as e:
            error_msg = f"{lang} 语言处理失败 - 请求ID: {request_id}, 错误: {str(e)}"
            logger.error(error_msg, exc_info=True)
            results.append(error_msg)
            # 继续处理其他语言,不中断整个流程
            continue
    
    logger.info(f"多语言内容处理完成 - 请求ID: {request_id}, 结果: {results}")
    return results

@router.post("/workflow/process")
async def process_workflow(request: FetchRequest):
    """完整的处理流程"""
    try:
        logger.info(f"开始完整处理流程: ID={request.id}, URL={request.url}, Languages={request.languages}")
        
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
        
        # 8. 处理多语言内容
        results = await process_multilingual_content(
            request.id,
            request.url,
            content,
            chapters,
            article,
            request.languages
        )
        
        return {
            "success": True,
            "message": "处理完成",
            "steps": [
                "获取视频信息成功",
                "获取章节信息成功",
                "处理作者信息成功",
                "创建文章成功",
                "获取字幕成功",
                *results  # 展开每种语言的处理结果
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