import requests
from concurrent.futures import ThreadPoolExecutor
from app.config import settings
from app.utils.logger import logger
from app.repositories.proxy import proxy_repository
from typing import List, Dict
import time

class ProxyTester:
    def __init__(self, proxies: List[str], timeout: int, test_url: str):
        self.proxies = proxies
        self.timeout = timeout
        self.test_url = test_url

    def test_single_proxy(self, proxy: str) -> Dict:
        """
        测试单个代理
        """
        try:
            start_time = time.time()
            response = requests.get(
                self.test_url,
                proxies={"http": proxy, "https": proxy},
                timeout=self.timeout,
                verify=False
            )
            response.raise_for_status()
            elapsed = time.time() - start_time
            
            return {
                "proxy": proxy,
                "status": "success",
                "response_time": elapsed
            }
        except Exception as e:
            return {
                "proxy": proxy,
                "status": "failed",
                "error": str(e)
            }

    async def run_tests(self) -> Dict:
        """
        异步运行所有代理测试
        """
        try:
            # 立即返回响应
            logger.info(f"开始测试 {len(self.proxies)} 个代理")
            
            # 在后台处理测试
            with ThreadPoolExecutor(max_workers=settings.PROXY_TEST_MAX_WORKERS) as executor:
                results = []
                for proxy in self.proxies:
                    result = executor.submit(self.test_single_proxy, proxy).result()
                    results.append(result)
                
                # 批量更新数据库
                proxy_repository.batch_create_or_update_proxies(results)
                    
            return {
                "status": "success",
                "message": "代理测试已在后台完成处理",
                "tested_count": len(self.proxies)
            }
            
        except Exception as e:
            logger.error(f"代理测试失败: {str(e)}", exc_info=True)
            raise 