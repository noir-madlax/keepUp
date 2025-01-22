from typing import Optional
from app.models.prompt import PromptModel
from app.repositories.supabase import SupabaseService
from app.utils.logger import logger

class PromptRepository:
    @staticmethod
    async def get_prompt_by_type(type: str) -> Optional[PromptModel]:
        """根据类型获取提示词
        
        Args:
            type: 提示词类型，如 'summary_en', 'summary_zh'
            
        Returns:
            Optional[PromptModel]: 提示词模型，如果不存在返回 None
        """
        try:
            client = SupabaseService.get_client()
            
            result = client.table('keep_prompt') \
                .select('*') \
                .eq('type', type) \
                .single() \
                .execute()
                
            if result.data:
                return PromptModel(**result.data)
            
            logger.warning(f"未找到类型为 {type} 的提示词")
            return None
            
        except Exception as e:
            logger.error(f"获取提示词失败: {str(e)}")
            return None 