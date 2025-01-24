import requests
from typing import List, Dict
from datetime import datetime
from app.utils.logger import logger
from app.config import settings
from app.repositories.supabase import SupabaseService
import asyncio

class ProxyGetter:
    def __init__(self):
        self.api_token = settings.WEBSHARE_API_TOKEN
        self.base_url = "https://proxy.webshare.io/api/v2/proxy/list"
        self.headers = {
            "Authorization": f"Token {self.api_token}"
        }

    def get_proxies(self, page: int = 1) -> Dict:
        """
        从Webshare获取代理列表
        """
        try:
            params = {"page": page}
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"获取代理列表失败: {str(e)}", exc_info=True)
            raise

    def format_proxies(self, proxy_data: List[Dict]) -> List[str]:
        """
        格式化代理列表为标准格式
        """
        return [f"http://{proxy['username']}:{proxy['password']}@{proxy['proxy_address']}:{proxy['ports']['http']}"
                for proxy in proxy_data]

    async def trigger_proxy_test(self, proxies: List[str]):
        """
        触发代理测试
        """
        try:
            # 异步触发代理测试
            response = requests.post(
                "https://keep-up-backend.vercel.app/router/test",  # 根据实际部署环境修改
                json={"proxies": proxies}
            )
            response.raise_for_status()
            logger.info(f"成功触发代理测试，代理数量: {len(proxies)}")
        except Exception as e:
            logger.error(f"触发代理测试失败: {str(e)}", exc_info=True)

    async def run(self) -> Dict:
        """
        运行代理获取流程
        """
        try:
            total_proxies = []
            page = 1
            
            while True:
                # 获取当前页的代理
                result = self.get_proxies(page)
                proxy_list = result.get("results", [])
                
                if not proxy_list:
                    break
                
                # 格式化代理列表
                formatted_proxies = self.format_proxies(proxy_list)
                total_proxies.extend(formatted_proxies)
                
                # 每获取一批就触发测试
                await self.trigger_proxy_test(formatted_proxies)
                
                # 检查是否还有下一页
                if not result.get("next"):
                    break
                    
                page += 1
                
            return {
                "status": "success",
                "message": f"成功获取并触发测试 {len(total_proxies)} 个代理",
                "total": len(total_proxies)
            }
            
        except Exception as e:
            logger.error(f"代理获取流程失败: {str(e)}", exc_info=True)
            raise 