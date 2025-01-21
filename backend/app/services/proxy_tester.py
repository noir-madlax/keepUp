import requests
import concurrent.futures
import time
import json
from datetime import datetime
from bs4 import BeautifulSoup
from app.utils.logger import logger
from app.config import settings

class ProxyTester:
    def __init__(self, proxies, timeout=10, test_url=None):
        self.proxies = proxies
        self.timeout = timeout
        self.test_url = test_url or settings.YOUTUBE_TEST_URL

    def test_single_proxy(self, proxy):
        proxies = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
        
        logger.info(f"开始测试代理: {proxy}")
        try:
            start_time = time.time()
            response = requests.get(
                self.test_url,
                proxies=proxies,
                timeout=self.timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            )
            elapsed_time = time.time() - start_time
            
            # 使用 BeautifulSoup 解析页面
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('meta', {'name': 'title'})
            
            if not title or not title.get('content'):
                raise ValueError("无法获取视频标题")
            
            result = {
                'proxy': proxy,
                'status': 'success',
                'response_time': round(elapsed_time, 2),
                'status_code': response.status_code,
                'title': title['content']
            }
            logger.info(f"代理测试成功: {proxy}, 响应时间: {result['response_time']}秒, 标题: {result['title']}")
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"代理测试失败: {proxy}, 错误: {error_msg}")
            return {
                'proxy': proxy,
                'status': 'failed',
                'error': error_msg
            }

    async def run_tests(self, max_workers=None):
        max_workers = max_workers or settings.PROXY_TEST_MAX_WORKERS
        logger.info(f"开始测试 {len(self.proxies)} 个代理...")
        logger.info(f"测试URL: {self.test_url}")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(self.test_single_proxy, self.proxies))
        
        return self.analyze_results(results)

    def analyze_results(self, results):
        valid_proxies = []
        invalid_proxies = []

        for result in results:
            if result['status'] == 'success' and 'title' in result:
                valid_proxies.append({
                    'proxy': result['proxy'],
                    'response_time': result['response_time'],
                    'title': result['title']
                })
            else:
                invalid_proxies.append({
                    'proxy': result['proxy'],
                    'error': result.get('error', 'Unknown error')
                })

        # 按响应时间排序有效代理
        valid_proxies.sort(key=lambda x: x['response_time'])
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'test_url': self.test_url,
            'total_tested': len(results),
            'valid_count': len(valid_proxies),
            'invalid_count': len(invalid_proxies),
            'valid_proxies': valid_proxies,
            'invalid_proxies': invalid_proxies
        }

        logger.info(f"测试完成，有效代理: {len(valid_proxies)}，无效代理: {len(invalid_proxies)}")
        return report 