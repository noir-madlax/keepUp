from fastapi import APIRouter, HTTPException
from app.models.request import FetchRequest
from app.services.content_fetcher.service import ContentFetcherService
from app.repositories.supabase import SupabaseService
from app.utils.logger import logger

router = APIRouter()

@router.post("/fetch-content")
async def fetch_content(request: FetchRequest):
    try:
        logger.info(f"收到获取内容请求: ID={request.id}, URL={request.url}")
        
        # 更新状态为处理中
        await SupabaseService.update_status(request.id, "processing")
        
        # 获取内容
        service = ContentFetcherService()
        content = await service.fetch_content(request.url)
        
        if not content:
            raise HTTPException(status_code=400, detail="无法获取内容")
        
        # 更新数据库
        await SupabaseService.update_content(request.id, content)
        
        return {"success": True, "message": "内容获取成功"}
        
    except Exception as e:
        logger.error(f"处理失败: {str(e)}", exc_info=True)
        await SupabaseService.update_status(
            request.id, 
            "failed", 
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e)) 