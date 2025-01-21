from typing import Optional, Dict
from app.utils.logger import logger
from datetime import datetime
from .supabase import SupabaseService
import time

class ProxyRepository:
    @classmethod
    async def get_available_proxy(cls) -> Optional[Dict[str, str]]:
        """获取一个可用的代理"""
        try:
            client = SupabaseService.get_client()
            
            # 按ID顺序获取代理
            result = client.table("keep_proxies")\
                .select("id", "proxy_url")\
                .eq("is_active", True)\
                .order("id", desc=False)\
                .limit(1)\
                .execute()
            
            if not result.data:
                logger.warning("没有可用的代理")
                return None
                
            proxy = result.data[0]
            proxy_id, proxy_url = proxy['id'], proxy['proxy_url']
            
            # 更新最后使用时间
            client.table("keep_proxies")\
                .update({"last_used_at": "now()", "updated_at": "now()"})\
                .eq("id", proxy_id)\
                .execute()
            
            # 返回代理配置
            return {
                'http': f'http://{proxy_url}',
                'https': f'http://{proxy_url}'
            }
            
        except Exception as e:
            logger.error(f"获取代理失败: {str(e)}", exc_info=True)
            return None
            
    @classmethod
    async def update_proxy_status(cls, proxy_url: str, success: bool, response_time: float = None):
        """更新代理状态"""
        try:
            client = SupabaseService.get_client()
            proxy_url = proxy_url.replace('http://', '')
            
            if success:
                # 成功时更新
                data = {
                    "success_count": client.table("keep_proxies").select("success_count").single().execute().data["success_count"] + 1,
                    "response_time": response_time,
                    "updated_at": "now()"
                }
                client.table("keep_proxies")\
                    .update(data)\
                    .eq("proxy_url", proxy_url)\
                    .execute()
            else:
                # 获取当前失败次数
                current = client.table("keep_proxies")\
                    .select("fail_count")\
                    .eq("proxy_url", proxy_url)\
                    .single()\
                    .execute()
                    
                new_fail_count = current.data["fail_count"] + 1
                
                # 失败时更新
                data = {
                    "fail_count": new_fail_count,
                    "is_active": new_fail_count < 5,  # 失败5次后禁用
                    "updated_at": "now()"
                }
                client.table("keep_proxies")\
                    .update(data)\
                    .eq("proxy_url", proxy_url)\
                    .execute()
                
        except Exception as e:
            logger.error(f"更新代理状态失败: {str(e)}", exc_info=True)

proxy_repository = ProxyRepository() 