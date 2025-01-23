from typing import Optional, Dict, Any
from app.utils.logger import logger
from app.repositories.supabase import SupabaseService

class LLMRecordsRepository:
    @staticmethod
    async def create_record(
        request_id: int,
        provider: str,
        model: str,
        prompt_type: str,
        input_content: str,
        output_content: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """创建LLM调用记录
        
        Args:
            request_id: 关联的请求ID
            provider: 提供商名称
            model: 模型名称
            prompt_type: 提示词类型
            input_content: 输入内容
            output_content: 输出内容，可选
            error_message: 错误信息，可选
            
        Returns:
            Optional[Dict[str, Any]]: 创建的记录，失败返回None
        """
        try:
            client = SupabaseService.get_client()
            
            data = {
                "request_id": request_id,
                "provider": provider,
                "model": model,
                "prompt_type": prompt_type,
                "input_content": input_content,
                "output_content": output_content,
                "error_message": error_message
            }
            
            result = client.table("keep_llm_records")\
                .insert(data)\
                .execute()
                
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"创建LLM记录失败: {str(e)}")
            return None

    @staticmethod
    async def get_records_by_request_id(request_id: int) -> list[Dict[str, Any]]:
        """获取指定请求ID的所有LLM调用记录
        
        Args:
            request_id: 请求ID
            
        Returns:
            list[Dict[str, Any]]: LLM调用记录列表
        """
        try:
            client = SupabaseService.get_client()
            
            result = client.table("keep_llm_records")\
                .select("*")\
                .eq("request_id", request_id)\
                .order("created_at", desc=True)\
                .execute()
                
            return result.data or []
            
        except Exception as e:
            logger.error(f"获取LLM记录失败: {str(e)}")
            return [] 