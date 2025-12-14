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
from app.services.private_content_service import PrivateContentService
from app.services.deep_research_service import DeepResearchService
from app.services.platform_parser.github import GitHubParser

import asyncio
import json
from typing import List, Optional

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
        error_msg = "Request record not found"
        await RequestLogger.error(request_id, Steps.SUMMARY_PROCESS, error_msg, Exception(error_msg))
        return [error_msg]
        
    # 获取文章信息
    article = await SupabaseService.get_article_by_request_id(request_id)
    if not article:
        error_msg = "Article record not found"
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
            
            # coze_response = await call_coze_and_parse(
            #     parse_request.url, 
            #     parse_request.content, 
            #     parse_request.chapters,
            #     workflow_id,
            #     request_id
            # )
            
            # await process_coze_result(
            #     coze_response, 
            #     request_id, 
            #     request.get('parsed_url'),
            #     article,
            #     lang
            # )
            
            msg = f"{lang} 内容处理完成"
            await RequestLogger.info(request_id, Steps.SUMMARY_PROCESS, msg)
            results.append(msg)
            
        except Exception as e:
            error_msg = f"{lang} language processing failed"
            await RequestLogger.error(request_id, Steps.SUMMARY_PROCESS, error_msg, e)
            results.append(error_msg)
            logger.error(f"Processing failed: {error_msg}, {e}")
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
            "Subtitle processing skipped"
        )
        return ["Subtitle processing skipped"]
    
    # 获取请求信息
    request = await SupabaseService.get_article_request(request_id)
    if not request:
        error_msg = "Request record not found"
        await RequestLogger.error(request_id, Steps.SUBTITLE_PROCESS, error_msg, Exception(error_msg))
        return [error_msg]
        
    # 获取文章信息
    article = await SupabaseService.get_article_by_request_id(request_id)
    if not article:
        error_msg = "Article record not found"
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
            error_msg = f"{lang} subtitle processing failed"
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
            "Detailed processing skipped"
        )
        return ["Detailed processing skipped"]
    
    # 获取请求信息
    request = await SupabaseService.get_article_request(request_id)
    if not request:
        error_msg = "Request record not found"
        await RequestLogger.error(request_id, Steps.DETAILED_PROCESS, error_msg, Exception(error_msg))
        return [error_msg]
        
    # 获取文章信息
    article = await SupabaseService.get_article_by_request_id(request_id)
    if not article:
        error_msg = "Article record not found"
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
            error_msg = f"{lang} detailed content processing failed"
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
                error_msg = "Unable to get video information"
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
                error_msg = "Unable to get subtitle content"
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


async def process_github_agent_task(request: FetchRequest):
    """
    GitHub Agent 项目分析后台任务
    
    使用 Gemini Deep Research API 分析 GitHub 项目，
    失败重试 1 次，然后按现有失败处理逻辑。
    
    Args:
        request: 包含 GitHub URL 的请求对象
    """
    MAX_RETRIES = 2  # 初次 + 1次重试
    
    try:
        await RequestLogger.info(
            request_id=request.id,
            step=Steps.PROCESS_START,
            message=f"开始 GitHub Agent 分析: URL={request.original_url}"
        )
        
        # 1. 提取项目名称作为标题
        project_title = GitHubParser.extract_project_name(request.original_url)
        
        # 2. 创建/获取作者信息
        author_name = "GitHub Agent Analysis"
        author = await SupabaseService.get_author_by_name(author_name)
        if not author:
            author = await SupabaseService.create_author({
                "name": author_name,
                "icon": "/images/icons/github.svg"
            })
        
        # 3. 创建文章基础记录（状态为 pending）
        # 使用字典直接插入，避免模型字段限制
        from app.repositories.supabase import SupabaseService as SupabaseClient
        client = SupabaseClient.get_client()
        
        article_insert_data = {
            "title": project_title,
            "content": "",
            "channel": "github",
            "original_link": request.original_url,
            "user_id": request.user_id,
            "author_id": author["id"],
            "is_visible": False,
            "cover_image_url": "/images/covers/article_default.png",
            "tags": ["GitHub", "Agent分析"]
        }
        
        try:
            # 直接使用 Supabase client 插入文章
            result = client.table("keep_articles").insert(article_insert_data).execute()
            if not result.data:
                raise ValueError("创建文章失败")
            article = result.data[0]
            
            await SupabaseService.update_article_id(request.id, article['id'])
            
            await RequestLogger.info(
                request.id,
                Steps.PROCESS_START,
                f"文章记录创建成功: article_id={article['id']}"
            )
        except Exception as e:
            error_msg = str(e)
            await RequestLogger.error(request.id, Steps.PROCESS_ERROR, error_msg, e)
            await SupabaseService.update_status(request.id, "failed", error_msg)
            return
        
        # 4. 调用 Deep Research API（含重试逻辑）
        research_result = None
        last_error = None
        
        for attempt in range(MAX_RETRIES):
            try:
                await RequestLogger.info(
                    request.id,
                    Steps.SUMMARY_PROCESS,
                    f"Deep Research 第 {attempt + 1} 次尝试..."
                )
                
                research_result = await DeepResearchService.run_deep_research(
                    github_url=request.original_url,
                    request_id=request.id
                )
                
                if research_result["success"]:
                    await RequestLogger.info(
                        request.id,
                        Steps.SUMMARY_PROCESS,
                        f"Deep Research 成功完成，耗时 {int(research_result['elapsed_seconds'])} 秒"
                    )
                    break
                else:
                    last_error = research_result.get("error", "未知错误")
                    await RequestLogger.info(
                        request.id,
                        Steps.SUMMARY_PROCESS,
                        f"Deep Research 第 {attempt + 1} 次失败: {last_error}"
                    )
                    
            except Exception as e:
                last_error = str(e)
                await RequestLogger.info(
                    request.id,
                    Steps.SUMMARY_PROCESS,
                    f"Deep Research 第 {attempt + 1} 次异常: {last_error}"
                )
            
            # 如果不是最后一次尝试，等待后重试
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(10)  # 等待 10 秒后重试
        
        # 5. 检查结果
        if not research_result or not research_result["success"]:
            error_msg = f"GitHub Agent 分析失败（已重试 {MAX_RETRIES} 次）: {last_error}"
            await RequestLogger.error(
                request.id,
                Steps.PROCESS_ERROR,
                error_msg,
                Exception(error_msg)
            )
            await SupabaseService.update_status(request.id, "failed", error_msg)
            return
        
        # 6. 保存分析报告到文章 sections
        report_content = research_result["report"]
        
        # 创建 "总结" section 存储完整报告
        sections = [
            {
                "article_id": article['id'],
                "section_type": "总结",
                "content": report_content,
                "language": "zh",
                "sort_order": 1
            }
        ]
        
        await SupabaseService.create_article_sections(article['id'], sections)
        
        await RequestLogger.info(
            request.id,
            Steps.SUMMARY_PROCESS,
            f"分析报告已保存，长度: {len(report_content)} 字符"
        )
        
        # 7. 更新文章为可见状态
        await SupabaseService.update_article_visibility(article['id'], True)
        
        # 8. 更新请求状态为完成
        await SupabaseService.update_status(request.id, "processed")
        
        # 9. 创建浏览记录
        await create_article_view_record(request.user_id, article['id'])
        
        await RequestLogger.info(
            request.id,
            Steps.PROCESS_COMPLETE,
            "GitHub Agent 分析完成",
            metadata={
                "article_id": article['id'],
                "report_length": len(report_content),
                "elapsed_seconds": research_result["elapsed_seconds"]
            }
        )
        
    except Exception as e:
        logger.error(f"GitHub Agent 分析失败: request_id={request.id}, error={str(e)}")
        await RequestLogger.error(
            request.id,
            Steps.PROCESS_ERROR,
            "GitHub Agent 分析异常",
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
        
        # 1. 检查URL是否重复 1-24日，暂时去掉
        # if await SupabaseService.check_url_exists(request.original_url):
        #     return {
        #         "success": False,
        #         "message": "URL已经存在"
        #     }
        
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
                error_msg = "Unable to parse URL"
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
        # GitHub 平台使用专用的 Deep Research 处理流程
        if platform == "github":
            background_tasks.add_task(process_github_agent_task, request)
        else:
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


async def process_private_content_task(
    request_id: int,
    user_id: str,
    input_type: str,
    prompt_type: str,
    title: str,
    content: str = None,
    audio_url: str = None
):
    """后台处理私密内容任务"""
    try:
        result = await PrivateContentService.process_private_content(
            request_id=request_id,
            user_id=user_id,
            input_type=input_type,
            prompt_type=prompt_type,
            title=title,
            content=content,
            audio_url=audio_url
        )
        
        if result:
            logger.info(f"私密内容处理完成: request_id={request_id}, article_id={result['article_id']}")
        else:
            logger.error(f"私密内容处理失败: request_id={request_id}")
            
    except Exception as e:
        logger.error(f"私密内容后台任务失败: {str(e)}")
        await SupabaseService.update_status(request_id, "failed", str(e))


@router.post("/workflow/private-upload")
async def private_upload_workflow(
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = None,
    text_content: str = Form(None),
    input_type: str = Form(...),  # 'audio' 或 'text'
    prompt_type: str = Form(default='general'),  # 'general', 'parent', 'customer'
    title: str = Form(default=''),
    user_id: str = Form(...)
):
    """处理私密内容上传请求
    
    支持两种输入方式：
    1. 音频文件上传 (input_type='audio')
    2. 文字内容输入 (input_type='text')
    
    Args:
        file: 音频文件（input_type='audio'时必需）
        text_content: 文字内容（input_type='text'时必需）
        input_type: 输入类型
        prompt_type: Prompt模版类型
        title: 内容标题
        user_id: 用户ID
    """
    try:
        audio_url = None
        content = None
        
        # 验证输入
        if input_type == 'audio':
            if not file:
                return {
                    "success": False,
                    "message": "音频模式下必须上传文件"
                }
            
            # 读取文件内容
            file_content = await file.read()
            
            # 验证音频文件
            is_valid, error_msg = PrivateContentService.validate_audio_file(
                file.filename,
                len(file_content)
            )
            if not is_valid:
                return {
                    "success": False,
                    "message": error_msg
                }
            
            # 上传到 Supabase Storage
            audio_url = await PrivateContentService.upload_audio_to_storage(
                file_content=file_content,
                filename=file.filename,
                user_id=user_id
            )
            
            if not audio_url:
                return {
                    "success": False,
                    "message": "音频文件上传失败"
                }
                
        elif input_type == 'text':
            if not text_content or not text_content.strip():
                return {
                    "success": False,
                    "message": "文字模式下必须输入内容"
                }
            content = text_content.strip()
            
            # 验证文字内容长度
            if len(content) < 50:
                return {
                    "success": False,
                    "message": "文字内容太短，请输入至少50个字符"
                }
            if len(content) > 100000:
                return {
                    "success": False,
                    "message": "文字内容超过限制，最多支持10万字符"
                }
        else:
            return {
                "success": False,
                "message": "无效的输入类型"
            }
        
        # 创建请求记录
        request_data = await PrivateContentService.create_private_request(
            user_id=user_id,
            input_type=input_type,
            prompt_type=prompt_type,
            title=title,
            original_url=audio_url or f'private://{input_type}'
        )
        
        if not request_data:
            return {
                "success": False,
                "message": "创建请求记录失败"
            }
        
        request_id = request_data['id']
        
        # 启动后台处理任务
        # 注意：title 保持原始值（可能为空），让 process_private_content 根据 AI 生成标题
        background_tasks.add_task(
            process_private_content_task,
            request_id=request_id,
            user_id=user_id,
            input_type=input_type,
            prompt_type=prompt_type,
            title=title,  # 保持原始值，空则由 AI 生成
            content=content,
            audio_url=audio_url
        )
        
        return {
            "success": True,
            "message": "私密内容已接收，开始处理",
            "request_id": request_id
        }
        
    except Exception as e:
        logger.error(f"私密内容上传处理失败: {str(e)}")
        return {
            "success": False,
            "message": str(e)
        }