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

    @classmethod
    async def inactive_history_proxies(cls, current_proxies: List[str]):
        """
        将不在当前批次中且 id>1000 的所有代理标记为非活跃
        分页获取所有代理并批量处理
        """
        try:
            client = SupabaseService.get_client()
            
            # 处理当前代理URL格式，移除 http:// 前缀
            current_proxies_processed = [proxy.replace('http://', '') for proxy in current_proxies]
            logger.info(f"当前活跃代理数量: {len(current_proxies_processed)}")

            # 分页获取所有 id>1000 的代理
            all_proxies = []
            page = 0
            page_size = 1000
            
            while True:
                result = client.table("keep_proxies")\
                    .select("id", "proxy_url")\
                    .gt("id", 1000)\
                    .range(page * page_size, (page + 1) * page_size - 1)\
                    .execute()
                
                if not result.data:
                    break
                    
                all_proxies.extend(result.data)
                page += 1
            
            logger.info(f"获取到的历史代理数量: {len(all_proxies)}")
                
            if not all_proxies:
                logger.info("没有需要处理的历史代理")
                return
                
            # 找出需要设置为非活跃的代理
            proxies_to_inactive = [
                proxy["id"] for proxy in all_proxies 
                if proxy["proxy_url"] not in current_proxies_processed  # 使用处理后的代理列表比较
            ]
            
            if not proxies_to_inactive:
                logger.info("没有需要设置为非活跃的代理")
                return
            
            logger.info(f"需要设置为非活跃的代理数量: {len(proxies_to_inactive)}")
                
            # 批量更新状态
            batch_size = 100  # 每批处理100个
            for i in range(0, len(proxies_to_inactive), batch_size):
                batch = proxies_to_inactive[i:i + batch_size]
                client.table("keep_proxies")\
                    .update({"is_active": False})\
                    .in_("id", batch)\
                    .execute()
                
            logger.info(f"成功更新代理状态，设置了 {len(proxies_to_inactive)} 个代理为非活跃")
            
        except Exception as e:
            logger.error(f"更新代理状态失败: {str(e)}", exc_info=True)

proxy_repository = ProxyRepository() 