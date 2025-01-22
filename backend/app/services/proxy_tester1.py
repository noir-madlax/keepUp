import requests
import concurrent.futures
import time
import json
from datetime import datetime
from bs4 import BeautifulSoup
from app.utils.logger import logger
from app.config import settings
from app.repositories.supabase import SupabaseService
from fastapi import HTTPException
import re
from urllib.parse import quote

class ProxyTester1:
    def __init__(self, timeout=10, test_url=None):
        # 2024-03-19: 移除proxies参数，改为从数据库读取
        self.timeout = timeout
        self.test_url = test_url or settings.YOUTUBE_TEST_URL
        self.client = SupabaseService.get_client()

    def validate_proxy_url(self, proxy_url: str) -> bool:
        """
        验证代理URL格式是否正确
        格式应为：username:password@host:port
        host可以是IP地址（xxx.xxx.xxx.xxx）或域名
        """
        # 2024-03-19: 更新代理URL格式验证，优化IP地址匹配
        # 用户名:密码@IP地址:端口
        ip_pattern = r'^[^:]+:[^@]+@(?:\d{1,3}\.){3}\d{1,3}:\d+$'
        # 用户名:密码@域名:端口
        domain_pattern = r'^[^:]+:[^@]+@[\w.-]+:\d+$'
        
        return bool(re.match(ip_pattern, proxy_url) or re.match(domain_pattern, proxy_url))

    def format_proxy_url(self, proxy_url: str) -> str:
        """
        格式化代理URL，确保正确编码和添加协议前缀
        格式：http://username:password@host:port
        """
        # 2024-03-19: 更新代理URL格式化，添加URL编码
        try:
            # 解析代理URL的各个部分
            auth, host_port = proxy_url.split('@')
            username, password = auth.split(':')
            
            # 对用户名和密码进行URL编码
            encoded_username = quote(username)
            encoded_password = quote(password)
            
            # 重新组装URL
            encoded_proxy = f"{encoded_username}:{encoded_password}@{host_port}"
            
            # 添加协议前缀
            if not encoded_proxy.startswith(('http://', 'https://')):
                return f'http://{encoded_proxy}'
            return encoded_proxy
            
        except Exception as e:
            logger.error(f"代理URL格式化失败: {proxy_url}, 错误: {str(e)}")
            return proxy_url  # 如果处理失败，返回原始URL

    async def get_proxies_from_db(self) -> list:
        """从数据库获取代理列表"""
        try:
            result = self.client.table("keep_proxies_list")\
                .select("proxy_url")\
                .eq("is_active", True)\
                .execute()
            
            if not result.data:
                logger.warning("数据库中没有找到活跃的代理")
                return []
            
            valid_proxies = []
            for item in result.data:
                proxy_url = item["proxy_url"]
                if not self.validate_proxy_url(proxy_url):
                    logger.warning(f"忽略格式不正确的代理URL: {proxy_url}")
                    continue
                valid_proxies.append(proxy_url)
            
            logger.info(f"从数据库获取了 {len(valid_proxies)} 个有效代理")
            return valid_proxies
            
        except Exception as e:
            logger.error(f"从数据库获取代理失败: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"获取代理列表失败: {str(e)}")

    def update_proxy_status(self, proxy: str, success: bool, response_time: float = None):
        """更新代理状态到数据库
        
        Args:
            proxy (str): 代理URL
            success (bool): 测试是否成功
            response_time (float, optional): 响应时间
        """
        try:
            # 获取当前代理状态
            current = self.client.table("keep_proxies_list")\
                .select("success_count,fail_count")\
                .eq("proxy_url", proxy)\
                .single()\
                .execute()
            
            if not current.data:
                logger.error(f"代理不存在: {proxy}")
                return
            
            # 准备更新数据
            update_data = {
                "is_active": success,
                "updated_at": "now()",
                "last_check_at": "now()"
            }
            
            if success:
                # 成功次数+1
                new_success_count = (current.data.get("success_count") or 0) + 1
                update_data.update({
                    "success_count": new_success_count,
                    "response_time": response_time
                })
            else:
                # 失败次数+1
                new_fail_count = (current.data.get("fail_count") or 0) + 1
                update_data.update({
                    "fail_count": new_fail_count
                })
            
            # 更新数据库
            self.client.table("keep_proxies_list")\
                .update(update_data)\
                .eq("proxy_url", proxy)\
                .execute()
            
            logger.info(
                f"代理状态更新成功: {proxy}, "
                f"状态: {'成功' if success else '失败'}, "
                f"{'成功次数: ' + str(new_success_count) if success else '失败次数: ' + str(new_fail_count)}"
            )
            
        except Exception as e:
            logger.error(f"更新代理状态失败: {proxy}, 错误: {str(e)}", exc_info=True)
            # 不抛出异常，避免影响测试流程
            return False
        
        return True

    def test_single_proxy(self, proxy):
        """测试单个代理
        
        Args:
            proxy (str): 代理URL
            
        Returns:
            dict: 测试结果
        """
        if not self.validate_proxy_url(proxy):
            logger.error(f"代理URL格式不正确: {proxy}")
            return {
                'proxy': proxy,
                'status': 'failed',
                'error': 'Proxy URL format is invalid'
            }

        formatted_proxy = self.format_proxy_url(proxy)
        proxies = {
            'http': formatted_proxy,
            'https': formatted_proxy
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
            
            # 检查响应状态码
            if response.status_code != 200:
                raise ValueError(f"HTTP状态码错误: {response.status_code}")
            
            # 使用 BeautifulSoup 解析页面
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('meta', {'name': 'title'})
            
            if not title or not title.get('content'):
                raise ValueError("无法获取视频标题")
            
            # 更新数据库状态
            update_success = self.update_proxy_status(proxy, True, elapsed_time)
            if not update_success:
                logger.warning(f"代理测试成功但状态更新失败: {proxy}")
            
            result = {
                'proxy': proxy,
                'status': 'success',
                'response_time': round(elapsed_time, 2),
                'status_code': response.status_code,
                'title': title['content']
            }
            logger.info(f"代理测试成功: {proxy}, 响应时间: {result['response_time']}秒, 标题: {result['title']}")
            return result
            
        except requests.exceptions.ConnectTimeout:
            error_msg = "连接超时"
            logger.error(f"代理测试失败: {proxy}, 错误: {error_msg}")
        except requests.exceptions.ReadTimeout:
            error_msg = "读取超时"
            logger.error(f"代理测试失败: {proxy}, 错误: {error_msg}")
        except requests.exceptions.ProxyError:
            error_msg = "代理连接错误"
            logger.error(f"代理测试失败: {proxy}, 错误: {error_msg}")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"代理测试失败: {proxy}, 错误: {error_msg}")
        
        # 更新数据库状态
        update_success = self.update_proxy_status(proxy, False)
        if not update_success:
            logger.warning(f"代理测试失败且状态更新失败: {proxy}")
        
        return {
            'proxy': proxy,
            'status': 'failed',
            'error': error_msg
        }

    async def run_tests(self, max_workers=None):
        max_workers = max_workers or settings.PROXY_TEST_MAX_WORKERS
        
        proxies = await self.get_proxies_from_db()
        logger.info(f"开始测试 {len(proxies)} 个代理...")
        logger.info(f"测试URL: {self.test_url}")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(self.test_single_proxy, proxies))
        
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