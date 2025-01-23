from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, Form
from app.models.request import FetchRequest, ParseRequest, AppendRequest
from app.services.content_fetcher.service import ContentFetcherService
from app.repositories.supabase import SupabaseService
from app.utils.logger import logger
from app.routers.parse import call_coze_and_parse, process_coze_result
from app.config import settings
from app.services.content_polisher import ContentPolisherService
from app.services.content_detailer import ContentDetailerService
from app.services.podcast_matcher import PodcastMatcher
from app.services.content_fetcher.youtube import YouTubeFetcher
from app.services.content_resolver import ContentResolver
from app.services.request_logger import RequestLogger, Steps
from app.utils.file_processor import process_file_content
from ..repositories.article_views import ArticleViewsRepository
from app.services.openrouter_service import OpenRouterService

import asyncio
import json
from typing import List

router = APIRouter()

async def process_summary_content(request_id: int, languages: list[str]) -> list[str]:
    """处理总结内容解析
    
    Args:
        request_id: 请求ID
        languages: 需要处理的语言列表
        
    Returns:
        list[str]: 处理结果信息列表
    """
    results = []
    await RequestLogger.info(
        request_id,
        Steps.SUMMARY_PROCESS,
        f"开始总结内容处理，语言列表: {languages}"
    )
    
    # 获取请求信息
    request = await SupabaseService.get_article_request(request_id)
    if not request:
        error_msg = "找不到请求记录"
        await RequestLogger.error(request_id, Steps.SUMMARY_PROCESS, error_msg, Exception(error_msg))
        return [error_msg]
        
    # 获取文章信息
    article = await SupabaseService.get_article_by_request_id(request_id)
    if not article:
        error_msg = "找不到文章记录"
        await RequestLogger.error(request_id, Steps.SUMMARY_PROCESS, error_msg, Exception(error_msg))
        return [error_msg]
    
    # 判断内容类型
    channel = article.get('channel')
    
    for lang in languages:
        # 根据内容类型和语言选择工作流ID
        if channel == 'webpage':
            workflow_id = (
                settings.COZE_WEB_SUMMARY_ID_ZH if lang == 'zh'
                else settings.COZE_WEB_SUMMARY_ID_EN
            )
        elif channel == 'file':
            workflow_id = (
                settings.COZE_FILE_SUMMARY_ID_ZH if lang == 'zh'
                else settings.COZE_FILE_SUMMARY_ID_EN
            )
        else:  # 视频类型
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
            # 调用 OpenRouter 获取摘要
            await RequestLogger.info(
                request_id,
                Steps.SUMMARY_PROCESS,
                f"开始调用 OpenRouter 处理 {lang} 语言摘要"
            )
            
            try:
                openrouter_summary = await OpenRouterService.get_summary(
                    content=request.get('content'),
                    request_id=request_id,
                    article_id=article['id'],
                    lang=lang
                )
                
                await RequestLogger.info(
                    request_id,
                    Steps.SUMMARY_PROCESS,
                    f"OpenRouter {lang} 语言摘要处理完成"
                )
                
            except Exception as e:
                await RequestLogger.error(
                    request_id,
                    Steps.SUMMARY_PROCESS,
                    f"OpenRouter {lang} 语言摘要处理失败: {str(e)}",
                    e
                )
                logger.error(f"OpenRouter处理失败: {str(e)}")
                raise e
            
            # 继续原有的 Coze 处理流程
            parse_request = ParseRequest(
                id=request_id, 
                url=request.get('url'),
                content=request.get('content'),
                chapters=request.get('chapters')
            )
            
            coze_response = await call_coze_and_parse(
                parse_request.url, 
                parse_request.content, 
                parse_request.chapters,
                workflow_id,
                request_id
            )
            
            await process_coze_result(
                coze_response, 
                request_id, 
                request.get('parsed_url'),
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
            logger.error(f"处理失败: {error_msg}, {e}")
            continue
    
    return results


async def process_subtitle_content(request_id: int, languages: list[str]) -> list[str]:
    """处理多语言字幕内容解析"""
    results = []
    
    # 如果只有 'na'，直接返回空结果
    if languages == ['na']:
        await RequestLogger.info(
            request_id,
            Steps.SUBTITLE_PROCESS,
            "字幕处理已跳过"
        )
        return ["字幕处理已跳过"]
    
    # 获取请求信息
    request = await SupabaseService.get_article_request(request_id)
    if not request:
        error_msg = "找不到请求记录"
        await RequestLogger.error(request_id, Steps.SUBTITLE_PROCESS, error_msg, Exception(error_msg))
        return [error_msg]
        
    # 获取文章信息
    article = await SupabaseService.get_article_by_request_id(request_id)
    if not article:
        error_msg = "找不到文章记录"
        await RequestLogger.error(request_id, Steps.SUBTITLE_PROCESS, error_msg, Exception(error_msg))
        return [error_msg]
    
    await RequestLogger.info(
        request_id,
        Steps.SUBTITLE_PROCESS,
        f"开始字幕内容处理，语言列表: {languages}"
    )
    
    for lang in languages:
        if lang == 'na':
            continue
            
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
                original_content=request.get('content'),
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

async def process_detailed_content(request_id: int, languages: list[str]) -> list[str]:
    """处理分段详述内容解析"""
    results = []
    
    # 如果只有 'na'，直接返回空结果
    if languages == ['na']:
        await RequestLogger.info(
            request_id,
            Steps.DETAILED_PROCESS,
            "分段详述处理已跳过"
        )
        return ["分段详述处理已跳过"]
    
    # 获取请求信息
    request = await SupabaseService.get_article_request(request_id)
    if not request:
        error_msg = "找不到请求记录"
        await RequestLogger.error(request_id, Steps.DETAILED_PROCESS, error_msg, Exception(error_msg))
        return [error_msg]
        
    # 获取文章信息
    article = await SupabaseService.get_article_by_request_id(request_id)
    if not article:
        error_msg = "找不到文章记录"
        await RequestLogger.error(request_id, Steps.DETAILED_PROCESS, error_msg, Exception(error_msg))
        return [error_msg]
    
    await RequestLogger.info(
        request_id,
        Steps.DETAILED_PROCESS,
        f"开始分段详述处理，语言列表: {languages}"
    )
    
    for lang in languages:
        if lang == 'na':
            continue
            
        workflow_id = (
            settings.COZE_DETAILED_WORKFLOW_ID_ZH if lang == 'zh'
            else settings.COZE_DETAILED_WORKFLOW_ID_EN
        )

        await RequestLogger.info(
            request_id,
            Steps.DETAILED_PROCESS,
            f"使用工作流 {workflow_id} 处理 {lang} 语言"
        )
        
        try:
            # 添加分段详述处理
            await ContentDetailerService.process_article_content(
                article_id=article['id'],
                chapters=request.get('chapters'),
                language=lang,
                workflow_id=workflow_id
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

async def process_multilingual_tasks(request_id: int, summary_languages: List[str], subtitle_languages: List[str], detailed_languages: List[str]) -> None:
    """处理多语言任务
    
    Args:
        request_id: 请求ID
        summary_languages: 需要处理的摘要语言列表
        subtitle_languages: 需要处理的字幕语言列表
        detailed_languages: 需要处理的详述语言列表
    """
    # 创建异步任务
    async with RequestLogger.step_context(request_id, Steps.SUMMARY_PROCESS):
        summary_task = asyncio.create_task(
            process_summary_content(
                request_id,
                summary_languages
            )
        )

    async with RequestLogger.step_context(request_id, Steps.SUBTITLE_PROCESS):
        subtitle_task = asyncio.create_task(
            process_subtitle_content(
                request_id,
                subtitle_languages
            )
        )

    # 等待summary_task完成
    summary_result = await summary_task

    async with RequestLogger.step_context(request_id, Steps.DETAILED_PROCESS):
        detailed_task = asyncio.create_task(
            process_detailed_content(
                request_id,
                detailed_languages
            )
        )

    # 等待所有任务完成
    results = await asyncio.gather(
        summary_task,
        subtitle_task,
        detailed_task,
        return_exceptions=True
    )
    
    # 获取文章信息
    article = await SupabaseService.get_article_by_request_id(request_id)
    if article:
        # 更新文章为可见状态
        await SupabaseService.update_article_visibility(article['id'], True)
    
    # 更新请求状态
    await SupabaseService.update_status(request_id, "processed")
    
    await RequestLogger.info(
        request_id,
        Steps.PROCESS_COMPLETE,
        "多语言处理完成",
        metadata={"results": results}
    )

async def process_article_task(request: FetchRequest):
    try:
        await RequestLogger.info(
            request_id=request.id,
            step=Steps.PROCESS_START,
            message=f"开始后台处理: URL={request.parsed_url}, Languages={request.summary_languages}"
        )
        
        # 2. 获取视频基础信息
        async with RequestLogger.step_context(request.id, Steps.VIDEO_INFO_FETCH):
            service = ContentFetcherService(request)
            video_info = await service.get_video_info(request.parsed_url)
            
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
            chapters = await service.get_chapters(request.parsed_url)
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
            # 添加 platform 和 original_url 到文章数据
            article_data.channel = request.platform  # 使用解析得到的 platform
            article_data.original_link = request.original_url  # 使用原始 URL
            article = await SupabaseService.create_article(article_data)
            
            # 更新请求记录的文章ID
            await SupabaseService.update_article_id(request.id, article['id'])
            
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
            content = await service.fetch_content(request.parsed_url)
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

        # 处理多语言任务
        await process_multilingual_tasks(
            request.id,
            request.summary_languages,
            request.subtitle_languages,
            request.detailed_languages
        )
        
        # 在创建文章成功后，添加浏览记录
        await create_article_view_record(request.user_id, article['id'])
        
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

async def create_article_view_record(user_id: str, article_id: int):
    """
    创建文章浏览记录
    
    Args:
        user_id: 用户ID
        article_id: 文章ID
    """
    try:
        await ArticleViewsRepository.create_article_view(
            user_id=user_id,
            article_id=article_id,
            is_author=True  # 上传时创建的记录，用户是作者
        )
        logger.info(f"创建文章浏览记录成功: user_id={user_id}, article_id={article_id}")
    except Exception as e:
        # 这里我们只记录错误，不抛出异常，因为这不是核心流程
        logger.error(f"创建文章浏览记录失败: {str(e)}", exc_info=True)

@router.post("/workflow/process")
async def process_workflow(request: FetchRequest, background_tasks: BackgroundTasks):
    """接收请求并立即返回"""
    try:
        
        # 1. 检查URL是否重复
        if await SupabaseService.check_url_exists(request.original_url):
            return {
                "success": False,
                "message": "URL已经存在"
            }
        
        # 2. 创建请求记录
        try:
            request_data = await SupabaseService.create_article_request({
                "original_url": request.original_url,
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
            result = await resolver.resolve(request.original_url)
            
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
        request.parsed_url = parsed_url
        request.platform = platform
        request.original_url = original_url
        
        # 7. 异步启动处理任务
        background_tasks.add_task(process_article_task, request)
        
        await RequestLogger.info(
            request.id,
            Steps.PROCESS_COMPLETE,
            "请求已接受,开始后台处理",
            metadata={
                "platform": platform,
                "parsed_url": parsed_url
            }
        )
        
        return {
            "success": True,
            "message": "请求已接受,开始后台处理",
            "request_id": request.id,
            "platform": platform,
            "parsed_url": parsed_url
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

@router.post("/workflow/upload")
async def upload_workflow(
    file: UploadFile,
    summary_languages: str = Form(...),
    user_id: str = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """处理文件上传请求"""
    try:
        # 1. 验证文件类型
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in ['pdf', 'doc', 'docx', 'txt']:
            return {
                "success": False,
                "message": "不支持的文件类型"
            }
            
        # 2. 验证文件大小（10MB限制）
        MAX_SIZE = 10 * 1024 * 1024  # 10MB
        content = await file.read()
        if len(content) > MAX_SIZE:
            return {
                "success": False,
                "message": "文件大小超过限制"
            }
                
        # 3. 创建请求记录
        request_data = await SupabaseService.create_article_request({
            "original_url": f"file://{file.filename}",  # 添加file://前缀
            "url": f"file://{file.filename}",
            "platform": "file", 
            "status": "pending",
            "user_id": user_id
        })
        request_id = request_data["id"]
        
        # 4. 处理文件内容
        text_content = await process_file_content(content, file_extension)
        
        if not text_content:
            await SupabaseService.update_status(request_id, "failed", "文件内容提取失败")
            return {
                "success": False,
                "message": "文件内容提取失败"
            }
        
        logger.info(f"文件内容提取成功: {len(text_content)} 字符")
            
        # 5. 创建处理请求对象
        file_request = FetchRequest(
            id=request_id,
            original_url=f"file://{file.filename}",
            parsed_url=f"file://{file.filename}",
            platform="file",
            content=text_content,  # 添加解析后的文本内容
            summary_languages=json.loads(summary_languages),
            subtitle_languages=["na"],
            detailed_languages=["na"],
            user_id=user_id
        )
        
        # 6. 异步启动处理任务
        background_tasks.add_task(process_article_task, file_request)
        
        return {
            "success": True,
            "message": "文件已接收，开始处理",
            "request_id": request_id
        }
        
    except Exception as e:
        logger.error(f"文件上传处理失败: {str(e)}")
        return {
            "success": False,
            "message": str(e)
        } 

@router.post("/workflow/append")
async def append_workflow(
    request: AppendRequest,
    background_tasks: BackgroundTasks
):
    """处理内容补充请求"""
    try:
        # 1. 获取原始请求信息
        request_id = await SupabaseService.get_request_id_by_article_id(request.article_id)
        if not request_id:
            raise HTTPException(status_code=404, detail="找不到原始文章请求")

        # 2. 启动后台处理任务
        background_tasks.add_task(
            process_multilingual_tasks,
            request_id,
            request.summary_languages,
            request.subtitle_languages,
            request.detailed_languages
        )
        
        return {
            "success": True,
            "message": "补充请求已接受，开始处理",
            "request_id": request_id
        }
        
    except Exception as e:
        logger.error(f"创建补充请求失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 