from contextlib import asynccontextmanager
import traceback
from typing import Optional
from app.services.supabase import SupabaseService
from app.models.log import LogCreate
from app.utils.logger import logger

class Steps:
    """处理步骤枚举"""
    PROCESS_START = "处理开始"
    URL_CHECK = "URL查重检查"
    REQUEST_CREATE = "创建请求记录"
    URL_RESOLVE = "URL解析"
    PLATFORM_UPDATE = "平台信息更新"
    VIDEO_INFO_FETCH = "获取视频信息"
    CONTENT_FETCH = "获取内容"
    SUMMARY_PROCESS = "处理摘要"
    SUBTITLE_PROCESS = "处理字幕"
    DETAILED_PROCESS = "处理详细内容"
    PROCESS_COMPLETE = "处理完成"
    PROCESS_ERROR = "处理错误"

class RequestLogger:
    """请求日志记录器"""
    
    @classmethod
    def log(
        cls,
        request_id: int,
        level: str,
        message: str,
        step: str,
        error_trace: Optional[str] = None,
        metadata: Optional[dict] = None
    ):
        """记录日志到数据库"""
        try:
            log_data = LogCreate(
                request_id=request_id,
                level=level,
                message=message,
                step=step,
                error_trace=error_trace,
                metadata=metadata
            )
            
            client = SupabaseService.get_client()
            result = client.table('keep_article_requests_logs').insert(log_data.dict()).execute()
            
            # 同时输出到控制台日志
            log_message = f"RequestID: {request_id} | Step: {step} | {message}"
            if level == "ERROR":
                logger.error(log_message)
            else:
                logger.info(log_message)
                
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"写入日志失败: {str(e)}", exc_info=True)

    @classmethod
    async def info(
        cls,
        request_id: int,
        step: str,
        message: str,
        metadata: Optional[dict] = None
    ):
        """记录信息级别日志"""
        return cls.log(request_id, "INFO", message, step, metadata=metadata)

    @classmethod
    async def error(
        cls,
        request_id: int,
        step: str,
        message: str,
        error: Exception,
        metadata: Optional[dict] = None
    ):
        """记录错误级别日志"""
        return cls.log(
            request_id,
            "ERROR",
            message,
            step,
            error_trace=traceback.format_exc(),
            metadata=metadata
        )

    @classmethod
    @asynccontextmanager
    async def step_context(cls, request_id: int, step: str):
        """步骤上下文管理器"""
        try:
            await cls.info(request_id, step, f"开始{step}")
            yield
            await cls.info(request_id, step, f"{step}完成")
        except Exception as e:
            await cls.error(request_id, step, f"{step}失败", e)
            raise