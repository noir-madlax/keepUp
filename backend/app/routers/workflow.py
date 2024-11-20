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
    """完整的处理流程：获取原文 -> 解析内容"""
    try:
        logger.info(f"开始完整处理流程: ID={request.id}, URL={request.url}")
        
        # 1. 更新状态为处理中
        await SupabaseService.update_status(request.id, "processing")
        
        # 2. 获取原文
        logger.info("步骤1: 获取原文")
        service = ContentFetcherService()
        content = await service.fetch_content(request.url)
        
        if not content:
            raise HTTPException(status_code=400, detail="无法获取原文内容")
        
        # 3. 保存原文
        logger.info("步骤2: 保存原文")
        await SupabaseService.update_content(request.id, content)
        
        # 4. 等待一小段时间确保数据已保存
        await asyncio.sleep(1)
        
        # 5. 调用解析服务（复用 parse.py 中的方法）
        logger.info("步骤3: 解析内容")
        parse_request = ParseRequest(id=request.id, url=request.url, content=content)
        coze_response = await call_coze_and_parse(parse_request.url, parse_request.content)
        
        # 6. 处理解析结果（复用 parse.py 中的方法）
        logger.info("步骤4: 保存解析结果")
        await process_coze_result(coze_response, request.id, request.url)
        
        return {
            "success": True, 
            "message": "处理完成",
            "steps": [
                "获取原文成功",
                "保存原文成功",
                "解析内容成功",
                "保存结果成功"
            ]
        }
        
    except Exception as e:
        logger.error(f"工作流处理失败: {str(e)}", exc_info=True)
        # 更新失败状态
        await SupabaseService.update_status(
            request.id, 
            "failed", 
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e)) 