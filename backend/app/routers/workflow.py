from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.request import FetchRequest, ParseRequest
from app.services.content_fetcher.service import ContentFetcherService
from app.services.supabase import SupabaseService
from app.utils.logger import logger
from app.routers.parse import call_coze_and_parse, process_coze_result
from app.config import settings
from app.services.content_polisher import ContentPolisherService
from app.services.content_detailer import ContentDetailerService
import asyncio

router = APIRouter()

async def process_summary_content(request_id: int, url: str, content: str, chapters: str, article, languages: list[str]) -> list[str]:
    """处理总结内容解析
    
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
    logger.info(f"开始总结内容处理 - 请求ID: {request_id}, 语言列表: {languages}")
    
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
    
    logger.info(f"总结内容处理完成 - 请求ID: {request_id}, 结果: {results}")
    return results


async def process_subtitle_content(request_id: int, url: str, content: str, chapters: str, article, languages: list[str]) -> list[str]:
    """处理多语言字幕内容解析
    
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
    logger.info(f"开始字幕内容处理 - 请求ID: {request_id}, 语言列表: {languages}")
    
    for lang in languages:
        
        polish_workflow_id = (
            settings.COZE_POLISH_WORKFLOW_ID_ZH if lang == 'zh'
            else settings.COZE_POLISH_WORKFLOW_ID_EN
        )

        logger.info(f"使用工作流 ID: {polish_workflow_id} 处理 {lang} 语言")
        
        try:
            
            # 添加内容润色处理
            await ContentPolisherService.process_article_content(
                article_id=article['id'],
                original_content=content,
                language=lang,
                workflow_id=polish_workflow_id
            )
            
            results.append(f"{lang} 内容处理完成")
            
        except Exception as e:
            error_msg = f"{lang} 语言处理失败 - 请求ID: {request_id}, 错误: {str(e)}"
            logger.error(error_msg, exc_info=True)
            results.append(error_msg)
            # 继续处理其他语言,不中断整个流程
            continue
    
    logger.info(f"字幕内容处理完成 - 请求ID: {request_id}, 结果: {results}")
    return results

async def process_detailed_content(request_id: int, url: str, content: str, chapters: str, article, languages: list[str]) -> list[str]:
    """处理分段详述内容
    
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
    logger.info(f"开始分段详述处理 - 请求ID: {request_id}, 语言列表: {languages}")
    
    for lang in languages:
        
        detailed_workflow_id = (
            settings.COZE_DETAILED_WORKFLOW_ID_ZH if lang == 'zh'
            else settings.COZE_DETAILED_WORKFLOW_ID_EN
        )

        logger.info(f"使用工作流 ID: {detailed_workflow_id} 处理 {lang} 语言")
        
        try:
            # 处理分段详述内容
            await ContentDetailerService.process_article_content(
                article_id=article['id'],
                chapters=chapters,
                language=lang,
                workflow_id=detailed_workflow_id
            )
            
            results.append(f"分段详述 - {lang} 内容处理完成")
            
        except Exception as e:
            error_msg = f"{lang} 分段详述处理失败 - 请求ID: {request_id}, 错误: {str(e)}"
            logger.error(error_msg, exc_info=True)
            results.append(error_msg)
            # 继续处理其他语言,不中断整个流程
            continue
    
    logger.info(f"分段详述处理完成 - 请求ID: {request_id}, 结果: {results}")
    return results

# 将原来的处理逻辑封装成一个独立的后台任务函数
async def process_article_task(request: FetchRequest):
    try:
        logger.info(f"开始后台处理: ID={request.id}, URL={request.url},"
                    f"Languages={request.summary_languages},"
                    f"Subtitle={request.subtitle_languages},"
                    f"Detailed={request.detailed_languages}"
                    )
        
        # 2. 获取视频基础信息
        service = ContentFetcherService()
        video_info = await service.get_video_info(request.url)
        
        if not video_info:
            logger.error(f"无法获取视频信息: ID={request.id}")
            await SupabaseService.update_status(request.id, "failed", "无法获取视频信息")
            return
            
        # 3. 获取视频章节信息
        chapters = await service.get_chapters(request.url)
        logger.info(f"获取到章节信息: {len(chapters) if chapters else 0} 个章节")
        
        # 保存章节信息到数据库
        await SupabaseService.update_chapters(request.id, chapters)
        
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
            logger.error(f"无法获取字幕内容: ID={request.id}")
            await SupabaseService.update_status(request.id, "failed", "无法获取字幕内容")
            return
        
        # 7. 保存字幕内容
        await SupabaseService.update_content(request.id, content)
        
        # 等待确保数据已保存
        await asyncio.sleep(1)
        
        # 创建异步任务
        summary_task = asyncio.create_task(
            process_summary_content(
                request.id,
                request.url,
                content,
                chapters,
                article,
                request.summary_languages
            )
        )
        
        subtitle_task = asyncio.create_task(
            process_subtitle_content(
                request.id,
                request.url,
                content,
                chapters,
                article,
                request.subtitle_languages
            )
        )
        
        # 等待字幕处理完成后再处理详述内容
        # TODO: 后续可以移除这个依赖，让detailed_task直接与其他任务并行
        await subtitle_task
        
        detailed_task = asyncio.create_task(
            process_detailed_content(
                request.id,
                request.url,
                content,
                chapters,
                article,
                request.detailed_languages
            )
        )
        
        # 等待所有任务完成
        results = await asyncio.gather(
            summary_task,
            detailed_task,
            return_exceptions=True
        )
        
        # 检查任务执行结果
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"任务执行出错: {str(result)}")
                raise result
        
        logger.info(f"后台处理完成: ID={request.id}")
        
    except Exception as e:
        logger.error(f"后台处理失败: ID={request.id}, Error={str(e)}", exc_info=True)
        await SupabaseService.update_status(
            request.id, 
            "failed", 
            error_message=str(e)
        )

@router.post("/workflow/process")
async def process_workflow(request: FetchRequest, background_tasks: BackgroundTasks):
    """接收请求并立即返回,在后台继续处理"""
    try:
        logger.info(f"收到处理请求: ID={request.id}, URL={request.url}")
        
        # 1. 更新状态为处理中
        await SupabaseService.update_status(request.id, "processing")
        
        # 将任务添加到后台处理队列
        background_tasks.add_task(process_article_task, request)
        
        return {
            "success": True,
            "message": "请求已接受,开始后台处理",
            "request_id": request.id
        }
        
    except Exception as e:
        logger.error(f"请求处理失败: {str(e)}", exc_info=True)
        await SupabaseService.update_status(
            request.id, 
            "failed", 
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e)) 