from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.request import FetchRequest, ParseRequest
from app.services.content_fetcher.service import ContentFetcherService
from app.services.supabase import SupabaseService
from app.utils.logger import logger
from app.routers.parse import call_coze_and_parse, process_coze_result
from app.config import settings
from app.services.content_polisher import ContentPolisherService
from app.services.content_detailer import ContentDetailerService
from app.services.podcast_matcher import PodcastMatcher
from app.services.content_fetcher.youtube import YouTubeFetcher
from app.services.content_resolver import ContentResolver
from app.services.request_logger import RequestLogger, Steps

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
        languages: 需要处理��语言列表
        
    Returns:
        list[str]: 处理结果信息列表
    """
    results = []
    await RequestLogger.info(
        request_id,
        Steps.SUMMARY_PROCESS,
        f"开始总结内容处理，语言列表: {languages}"
    )
    
    # 判断是否是网页内容
    is_webpage = article.get('channel') == 'webpage'
    
    for lang in languages:
        # 根据内容类型和语言选择工作流ID
        if is_webpage:
            workflow_id = (
                settings.COZE_WEB_SUMMARY_ID_ZH if lang == 'zh'
                else settings.COZE_WEB_SUMMARY_ID_EN
            )
        else:
            workflow_id = (
                settings.COZE_WORKFLOW_ID_ZH if lang == 'zh'
                else settings.COZE_WORKFLOW_ID_EN
            )
            
        await RequestLogger.info(
            request_id,
            Steps.SUMMARY_PROCESS,
            f"使用工作流 {workflow_id} 处理 {lang} 语言"
        )
        
        try:
            parse_request = ParseRequest(
                id=request_id, 
                url=url, 
                content=content, 
                chapters=chapters
            )
            
            coze_response = await call_coze_and_parse(
                parse_request.url, 
                parse_request.content, 
                parse_request.chapters,
                workflow_id
            )
            
            await process_coze_result(
                coze_response, 
                request_id, 
                url,
                article,
                lang
            )
            
            msg = f"{lang} 内容处理完成"
            await RequestLogger.info(request_id, Steps.SUMMARY_PROCESS, msg)
            results.append(msg)
            
        except Exception as e:
            error_msg = f"{lang} 语言处理失败"
            await RequestLogger.error(request_id, Steps.SUMMARY_PROCESS, error_msg, e)
            results.append(error_msg)
            continue
    
    return results


async def process_subtitle_content(request_id: int, url: str, content: str, chapters: str, article, languages: list[str]) -> list[str]:
    """处理多语言字幕内容解析"""
    results = []
    await RequestLogger.info(
        request_id,
        Steps.SUBTITLE_PROCESS,
        f"开始字幕内容处理，语言列表: {languages}"
    )
    
    for lang in languages:
        polish_workflow_id = (
            settings.COZE_POLISH_WORKFLOW_ID_ZH if lang == 'zh'
            else settings.COZE_POLISH_WORKFLOW_ID_EN
        )

        await RequestLogger.info(
            request_id,
            Steps.SUBTITLE_PROCESS,
            f"使用工作流 {polish_workflow_id} 处理 {lang} 语言"
        )
        
        try:
            # 添加内容润色处理
            await ContentPolisherService.process_article_content(
                article_id=article['id'],
                original_content=content,
                language=lang,
                workflow_id=polish_workflow_id
            )
            
            msg = f"{lang} 字幕内容处理完成"
            await RequestLogger.info(request_id, Steps.SUBTITLE_PROCESS, msg)
            results.append(msg)
            
        except Exception as e:
            error_msg = f"{lang} 字幕处理失败"
            await RequestLogger.error(request_id, Steps.SUBTITLE_PROCESS, error_msg, e)
            results.append(error_msg)
            continue
    
    return results

async def process_detailed_content(request_id: int, url: str, content: str, chapters: str, article, languages: list[str]) -> list[str]:
    """处理分段详述内容"""
    results = []
    await RequestLogger.info(
        request_id,
        Steps.DETAILED_PROCESS,
        f"开始分段详述处理，语言列表: {languages}"
    )
    
    for lang in languages:
        detailed_workflow_id = (
            settings.COZE_DETAILED_WORKFLOW_ID_ZH if lang == 'zh'
            else settings.COZE_DETAILED_WORKFLOW_ID_EN
        )

        await RequestLogger.info(
            request_id,
            Steps.DETAILED_PROCESS,
            f"使用工作流 {detailed_workflow_id} 处理 {lang} 语言"
        )
        
        try:
            # 处理分段详述内容
            await ContentDetailerService.process_article_content(
                article_id=article['id'],
                chapters=chapters,
                language=lang,
                workflow_id=detailed_workflow_id
            )
            
            msg = f"{lang} 分段详述处理完成"
            await RequestLogger.info(request_id, Steps.DETAILED_PROCESS, msg)
            results.append(msg)
            
        except Exception as e:
            error_msg = f"{lang} 分段详述处理失败"
            await RequestLogger.error(request_id, Steps.DETAILED_PROCESS, error_msg, e)
            results.append(error_msg)
            continue
    
    return results

# 将原来的处理逻辑封装成一个独立的后台任务函数
async def process_article_task(request: FetchRequest):
    try:
        await RequestLogger.info(
            request_id=request.id,
            step=Steps.PROCESS_START,
            message=f"开始后台处理: URL={request.url}, Languages={request.summary_languages}"
        )
        
        # 2. 获取视频基础信息
        async with RequestLogger.step_context(request.id, Steps.VIDEO_INFO_FETCH):
            service = ContentFetcherService()
            video_info = await service.get_video_info(request.url)
            
            if not video_info:
                error_msg = "无法获取视频信息"
                await RequestLogger.error(
                    request.id,
                    Steps.VIDEO_INFO_FETCH,
                    error_msg,
                    Exception(error_msg)
                )
                await SupabaseService.update_status(request.id, "failed", error_msg)
                return
        
        # 3. 获取视频章节信息
        async with RequestLogger.step_context(request.id, Steps.CONTENT_FETCH):
            chapters = await service.get_chapters(request.url)
            await RequestLogger.info(
                request.id,
                Steps.CONTENT_FETCH,
                f"获取到章节信息: {len(chapters) if chapters else 0} 个章节"
            )
            
            # 保存章信息到数据库
            await SupabaseService.update_chapters(request.id, chapters)
        
        # 4. 处理作者信息
        author = await SupabaseService.get_author_by_name(video_info.author["name"])
        if not author:
            # 创建新作者
            author = await SupabaseService.create_author(video_info.author)
        else:
            # 更新作者信息
            await SupabaseService.update_author(author["id"], video_info.author)
            
        # 5. 创建文章基础信息
        try:
            article_data = video_info.article
            article_data.author_id = author["id"]
            article = await SupabaseService.create_article(article_data)
        except ValueError as e:
            error_msg = str(e)
            await RequestLogger.error(
                request.id,
                Steps.PROCESS_ERROR,
                error_msg,
                e
            )
            await SupabaseService.update_status(request.id, "failed", error_msg)
            return
        
        # 6. 获取视频字幕
        async with RequestLogger.step_context(request.id, Steps.CONTENT_FETCH):
            content = await service.fetch_content(request.url)
            if not content:
                error_msg = "无法获取字幕内容"
                await RequestLogger.error(
                    request.id,
                    Steps.CONTENT_FETCH,
                    error_msg,
                    Exception(error_msg)
                )
                await SupabaseService.update_status(request.id, "failed", error_msg)
                return
            
            # 保存字幕内容
            await SupabaseService.update_content(request.id, content)
        
        # 等待确保数据已保存
        await asyncio.sleep(1)

        # 创建异步任务
        async with RequestLogger.step_context(request.id, Steps.SUMMARY_PROCESS):
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

        async with RequestLogger.step_context(request.id, Steps.SUBTITLE_PROCESS):
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

        # 等待summary_task完成
        summary_result = await summary_task

        async with RequestLogger.step_context(request.id, Steps.DETAILED_PROCESS):
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
            subtitle_task,
            detailed_task,
            return_exceptions=True
        )
        
        await RequestLogger.info(
            request.id,
            Steps.PROCESS_COMPLETE,
            "后台处理完成",
            metadata={"results": results}
        )
        
    except Exception as e:
        logger.error(f"后台处理失败: request_id={request.id}, error={str(e)}")
        await RequestLogger.error(
            request.id,
            Steps.PROCESS_ERROR,
            "后台处理失败",
            e
        )
        
        await SupabaseService.update_status(
            request.id, 
            "failed", 
            error_message=str(e)
        )

@router.post("/workflow/process")
async def process_workflow(request: FetchRequest, background_tasks: BackgroundTasks):
    """接收请求并立即返回"""
    try:
        
        # 1. 检查URL是否重复
        if await SupabaseService.check_url_exists(request.url):
            return {
                "success": False,
                "message": "URL已经存在"
            }
        
        # 2. 创建请求记录
        try:
            request_data = await SupabaseService.create_article_request({
                "original_url": request.url,
                "platform": "pending", 
                "status": "pending",
                "user_id": request.user_id
            })
            request.id = request_data["id"]
            
            await RequestLogger.info(
                request.id,
                Steps.REQUEST_CREATE,
                "创建请求记录成功",
                metadata={"request_id": request.id}
            )
        except Exception as e:
            await RequestLogger.error(0, Steps.REQUEST_CREATE, "创建请求记录失败", e)
            return {
                "success": False,
                "message": "创建请求记录失败"
            }
        
        # 3. 使用 ContentResolver 解析 URL
        async with RequestLogger.step_context(request.id, Steps.URL_RESOLVE):
            resolver = ContentResolver()
            result = await resolver.resolve(request.url)
            
            if not result:
                error_msg = "无法解析URL或找不到对应的YouTube内容"
                await RequestLogger.error(
                    request.id,
                    Steps.URL_RESOLVE,
                    error_msg,
                    Exception(error_msg)
                )
                await SupabaseService.update_status(request.id, "failed", error_msg)
                return {
                    "success": False,
                    "message": error_msg,
                    "request_id": request.id
                }
        
        platform, parsed_url, original_url = result
        
        # 4. 更新平台信息
        await SupabaseService.update_request_platform(
            request_id=request.id,
            platform=platform,
            parsed_url=parsed_url,
            original_url=original_url
        )
        
        # 5. 更新状态为处理中
        await SupabaseService.update_status(request.id, "processing")
        
        # 6. 使用解析后的URL更新请求对象
        request.url = parsed_url
        
        # 7. 异步启动处理任务，但不等待其完成
        # 将任务添加到后台处理队列
        background_tasks.add_task(process_article_task, request)
        
        await RequestLogger.info(
            request.id,
            Steps.PROCESS_COMPLETE,
            "请求已接受,开始后台处理",
            metadata={
                "platform": platform,
                "parsed_url": parsed_url if parsed_url != original_url else None
            }
        )
        
        return {
            "success": True,
            "message": "请求已接受,开始后台处理",
            "request_id": request.id,
            "platform": platform,
            "parsed_url": parsed_url if parsed_url != original_url else None
        }
        
    except Exception as e:
        request_id = getattr(request, 'id', 0)
        await RequestLogger.error(request_id, Steps.PROCESS_ERROR, "请求处理失败", e)
        if request_id:
            await SupabaseService.update_status(
                request_id,
                "failed",
                error_message=str(e)
            )
        raise HTTPException(status_code=500, detail=str(e)) 