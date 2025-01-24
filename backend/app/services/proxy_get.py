import requests
from typing import List, Dict
from datetime import datetime
from app.utils.logger import logger
from app.config import settings
from app.repositories.supabase import SupabaseService

class ProxyGetter:
    def __init__(self):
        self.api_url = "https://proxy.webshare.io/api/v2/proxy/list/"
        # 2024-03-19: Token处理说明
        # 本地开发：直接在.env中设置WEBSHARE_API_TOKEN="你的token"
        # 服务器部署：通过Vercel环境变量设置WEBSHARE_API_TOKEN
        self.headers = {
            "Authorization": f"Token {settings.WEBSHARE_API_TOKEN}"
        }

    async def fetch_proxies(self) -> List[Dict]:
        """从Webshare获取代理列表"""
        try:
            # 获取第一页，了解总数
            params = {
                "mode": "direct",
                "page": 1,
                "page_size": 100
            }
            
            response = requests.get(
                self.api_url,
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            total_pages = (data.get('count', 0) + params['page_size'] - 1) // params['page_size']
            
            # 收集所有代理
            all_proxies = []
            for page in range(1, total_pages + 1):
                params['page'] = page
                response = requests.get(
                    self.api_url,
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                
                page_data = response.json()
                proxies = page_data.get('results', [])
                all_proxies.extend(proxies)
                
                logger.info(f"获取第 {page}/{total_pages} 页代理，本页数量: {len(proxies)}")
            
            return all_proxies
            
        except Exception as e:
            logger.error(f"获取代理列表失败: {str(e)}", exc_info=True)
            raise

    async def save_proxies(self, proxies: List[Dict]) -> None:
        """保存代理到数据库"""
        try:
            client = SupabaseService.get_client()
            
            # 2024-03-19: 先获取现有代理列表，用于统计新增和重复数量
            existing_proxies = client.table("keep_proxies_list").select("proxy_url").execute()
            existing_proxy_urls = set(item['proxy_url'] for item in existing_proxies.data)
            
            # 准备插入数据
            proxy_data = []
            new_count = 0
            duplicate_count = 0
            
            for proxy in proxies:
                # 构建代理URL
                proxy_url = f"{proxy['username']}:{proxy['password']}@{proxy['proxy_address']}:{proxy['port']}"
                
                # 统计新增和重复的数量
                if proxy_url in existing_proxy_urls:
                    duplicate_count += 1
                else:
                    new_count += 1
                
                proxy_data.append({
                    "proxy_url": proxy_url,
                    "is_active": "true",
                    "fail_count": 0,
                    "success_count": 0,
                    "created_at": "now()",
                    "updated_at": "now()"
                })
            
            # 2024-03-19: 修改upsert逻辑，保留已存在代理的状态和统计数据
            result = client.table("keep_proxies_list").upsert(
                proxy_data,
                on_conflict="proxy_url",
                # 只在插入新记录时设置这些字段，已存在的记录保持不变
                ignore_duplicates=["is_active", "fail_count", "success_count"]
            ).execute()
            
            logger.info(f"代理保存统计:")
            logger.info(f"- 总处理数量: {len(proxy_data)} 个代理")
            logger.info(f"- 新增代理数: {new_count} 个")
            logger.info(f"- 重复代理数: {duplicate_count} 个")
            
            return {
                "total": len(proxy_data),
                "new": new_count,
                "duplicate": duplicate_count,
                "data": result.data
            }
            
        except Exception as e:
            logger.error(f"保存代理到数据库失败: {str(e)}", exc_info=True)
            raise

    async def run(self) -> Dict:
        """运行代理获取和保存流程"""
        try:
            # 1. 获取代理列表
            proxies = await self.fetch_proxies()
            logger.info(f"成功获取 {len(proxies)} 个代理")
            
            # 2. 保存到数据库
            save_result = await self.save_proxies(proxies)
            
            return {
                "success": True,
                "message": f"代理更新完成 - 总数: {save_result['total']}, 新增: {save_result['new']}, 重复: {save_result['duplicate']}",
                "stats": save_result
            }
            
        except Exception as e:
            error_msg = f"代理获取流程失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "message": error_msg,
                "total": 0
            } 