from http.server import BaseHTTPRequestHandler
import json
import os
import time
import threading
import logging
from supabase import create_client, Client
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_supabase_client() -> Client:
    """获取 Supabase 客户端实例"""
    url = os.getenv("VITE_SUPABASE_URL")
    key = os.getenv("VITE_SUPABASE_SERVICE_ROLE_KEY")
    
    logger.info(f"Supabase URL: {url}")
    logger.info(f"Using service role key")
    
    if not url or not key:
        raise ValueError("Missing VITE_SUPABASE_URL or VITE_SUPABASE_SERVICE_ROLE_KEY environment variables")
    
    return create_client(url, key)

def handle_request_processing(request_id: int) -> None:
    """处理请求的具体逻辑"""
    try:
        logger.info(f"开始处理请求 ID: {request_id}")
        
        # 模拟处理过程
        time.sleep(5)
        
        # 更新状态为已处理
        supabase = get_supabase_client()
        data = supabase.table('keep_article_requests').update({
            'status': 'processed'
        }).eq('id', request_id).execute()
        
        logger.info(f"请求 {request_id} 处理完成")
        logger.info(data)
        
    except Exception as e:
        logger.error(f"处理失败: {str(e)}", exc_info=True)
        try:
            supabase = get_supabase_client()
            supabase.table('keep_article_requests').update({
                'status': 'failed',
                'error_message': str(e)
            }).eq('id', request_id).execute()
        except Exception as update_error:
            logger.error(f"更新失败状态时出错: {str(update_error)}")

def process_content_async(url: str, content: str, request_id: int):
    """异步处理内容的函数"""
    try:
        logger.info(f"开始处理请求 ID: {request_id}")
        logger.info(f"URL: {url}")
        logger.info(f"Content 长度: {len(content) if content else 0}")
        
        start_time = time.time()
        
        # 调用具体的处理逻辑
        handle_request_processing(request_id)
        
        # 记录处理时间
        process_time = time.time() - start_time
        logger.info(f"处理完成，耗时: {process_time:.2f}秒")

    except Exception as e:
        logger.error(f"处理失败: {str(e)}", exc_info=True)
        try:
            supabase = get_supabase_client()
            supabase.table('keep_article_requests').update({
                'status': 'failed',
                'error_message': str(e)
            }).eq('id', request_id).execute()
        except Exception as update_error:
            logger.error(f"更新失败状态时出错: {str(update_error)}")

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            logger.info("收到新的解析请求")
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            url = data.get('url')
            content = data.get('content')
            request_id = data.get('id')

            logger.info(f"请求参数: id={request_id}, url={url}")

            # 立即返回成功响应
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'success': True,
                'message': '请求已接收，正在后台处理',
                'request_id': request_id
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))

            # 启动异步处理
            thread = threading.Thread(
                target=process_content_async,
                args=(url, content, request_id)
            )
            thread.start()
            logger.info("后台处理线程已启动")

        except Exception as e:
            logger.error(f"请求处理失败: {str(e)}", exc_info=True)
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'success': False,
                'message': str(e)
            }
            self.wfile.write(json.dumps(response).encode('utf-8')) 