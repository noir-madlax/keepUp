from typing import Optional, Dict, List
from app.utils.logger import logger
from datetime import datetime
from .supabase import SupabaseService
import time
import random

class ProxyRepository:
    @classmethod
    async def get_available_proxy(cls) -> Optional[Dict[str, str]]:
        """获取一个随机可用的代理"""
        try:
            client = SupabaseService.get_client()
            
            # 使用 id 来随机获取，因为 id 是连续的
            # 先获取最大和最小 id
            result = client.table("keep_proxies")\
                .select("id")\
                .eq("is_active", True)\
                .execute()
            
            if not result.data:
                logger.warning("没有可用的代理")
                return None
            
            # 从可用的代理中随机选择一个 id
            proxy_ids = [proxy['id'] for proxy in result.data]
            random_id = random.choice(proxy_ids)
            
            # 获取随机选择的代理
            result = client.table("keep_proxies")\
                .select("id", "proxy_url")\
                .eq("id", random_id)\
                .single()\
                .execute()
                
            if not result.data:
                logger.warning("没有可用的代理")
                return None
                
            proxy = result.data
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
    def create_or_update_proxy(cls, proxy_url: str, is_valid: bool, response_time: float = None) -> None:
        """
        创建或更新代理记录
        """
        try:
            client = SupabaseService.get_client()
            proxy_url = proxy_url.replace('http://', '')
            
            # 查找现有记录
            result = client.table("keep_proxies")\
                .select("*")\
                .eq("proxy_url", proxy_url)\
                .execute()
                
            if result.data:
                # 更新现有记录
                proxy = result.data[0]
                if is_valid:
                    data = {
                        "success_count": proxy.get("success_count", 0) + 1,
                        "is_active": True,
                        "response_time": response_time,
                        "updated_at": "now()"
                    }
                else:
                    new_fail_count = proxy.get("fail_count", 0) + 1
                    data = {
                        "fail_count": new_fail_count,
                        "is_active": False, 
                        "updated_at": "now()"
                    }
                
                client.table("keep_proxies")\
                    .update(data)\
                    .eq("proxy_url", proxy_url)\
                    .execute()
            else:
                # 创建新记录
                data = {
                    "proxy_url": proxy_url,
                    "is_active": is_valid,
                    "success_count": 1 if is_valid else 0,
                    "fail_count": 0 if is_valid else 1,
                    "response_time": response_time if is_valid else None,
                    "created_at": "now()",
                    "updated_at": "now()"
                }
                client.table("keep_proxies")\
                    .insert(data)\
                    .execute()
                
        except Exception as e:
            logger.error(f"创建或更新代理记录失败: {str(e)}", exc_info=True)
            raise

    @classmethod
    def batch_create_or_update_proxies(cls, proxy_results: List[Dict]) -> None:
        """
        批量创建或更新代理记录
        """
        try:
            for result in proxy_results:
                proxy_url = result["proxy"]
                is_valid = result["status"] == "success"
                response_time = result.get("response_time")
                cls.create_or_update_proxy(proxy_url, is_valid, response_time)
                
        except Exception as e:
            logger.error(f"批量更新代理记录失败: {str(e)}", exc_info=True)
            raise

    @classmethod
    async def update_proxy_status(cls, proxy_url: str, success: bool, response_time: float = None):
        """更新代理状态"""
        try:
            client = SupabaseService.get_client()
            proxy_url = proxy_url.replace('http://', '')
            
            if success:
                # 先获取当前代理的成功次数
                current = client.table("keep_proxies")\
                    .select("success_count")\
                    .eq("proxy_url", proxy_url)\
                    .single()\
                    .execute()
                    
                new_success_count = current.data["success_count"] + 1
                
                # 成功时更新
                data = {
                    "success_count": new_success_count,
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
                    "is_active": new_fail_count < 2,  # 失败2次后禁用
                    "updated_at": "now()"
                }
                client.table("keep_proxies")\
                    .update(data)\
                    .eq("proxy_url", proxy_url)\
                    .execute()
                
        except Exception as e:
            logger.error(f"更新代理状态失败: {str(e)}", exc_info=True)

proxy_repository = ProxyRepository() 