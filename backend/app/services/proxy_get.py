import requests
from typing import List, Dict
from datetime import datetime, timedelta
from app.utils.logger import logger
from app.config import settings
from app.repositories.proxy import proxy_repository

class ProxyGetter:
    def __init__(self):
        self.api_token = settings.WEBSHARE_API_TOKEN
        self.base_url = "https://proxy.webshare.io/api/v2/proxy/list/"
        self.headers = {
            "Authorization": f"Token {self.api_token}"
        }

    def get_proxies(self, page: int = 1) -> Dict:
        """
        从Webshare获取代理列表
        """
        try:
            params = {
                "mode": "direct",
                "page": page,
                "page_size": 100
            }
            
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            data = response.json()
            # 打印返回的数据结构
            logger.debug(f"API返回数据: {data}")
            return data
            
        except Exception as e:
            logger.error(f"获取代理列表失败: {str(e)}", exc_info=True)
            raise

    def format_proxies(self, proxy_data: List[Dict]) -> List[str]:
        """
        格式化代理列表为标准格式
        """
        formatted_proxies = []
        for proxy in proxy_data:
            try:
                # 打印单个代理数据
                logger.debug(f"处理代理数据: {proxy}")
                # 使用 get 方法安全获取数据
                username = proxy.get('username')
                password = proxy.get('password')
                address = proxy.get('proxy_address')
                port = proxy.get('port')  # 假设直接是port而不是ports字典
                
                if all([username, password, address, port]):
                    proxy_url = f"http://{username}:{password}@{address}:{port}"
                    formatted_proxies.append(proxy_url)
                else:
                    logger.warning(f"代理数据不完整: {proxy}")
                    
            except Exception as e:
                logger.error(f"格式化代理失败: {str(e)}", exc_info=True)
                continue
                
        return formatted_proxies

    async def trigger_proxy_test(self, proxies: List[str]):
        """
        触发代理测试
        """
        try:
            response = requests.post(
                "https://keep-up-backend.vercel.app/router/test",
                json=proxies  # 直接发送列表，不要包装成字典
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
            
            # 更新所有代理的状态
            await proxy_repository.inactive_history_proxies(total_proxies)
                
            return {
                "status": "success",
                "message": f"成功获取并触发测试 {len(total_proxies)} 个代理",
                "total": len(total_proxies)
            }
            
        except Exception as e:
            logger.error(f"代理获取流程失败: {str(e)}", exc_info=True)
            raise 