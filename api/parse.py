from http.server import BaseHTTPRequestHandler
import json
import os
import time
import threading
import logging
import requests
from supabase import create_client, Client
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)

# 添加一个处理器确保输出到 stderr
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)

def get_supabase_client() -> Client:
    """获取 Supabase 客户端实例"""
    url = os.getenv("VITE_SUPABASE_URL")
    key = os.getenv("VITE_SUPABASE_SERVICE_ROLE_KEY")
    
    logger.info(f"Supabase URL: {url}")
    logger.info(f"Using service role key")
    
    if not url or not key:
        raise ValueError("Missing VITE_SUPABASE_URL or VITE_SUPABASE_SERVICE_ROLE_KEY environment variables")
    
    return create_client(url, key)

def call_coze_api(url: str, content: str) -> dict:
    """调用 Coze API"""
    coze_api_url = "https://api.coze.com/v1/workflow/run"
    coze_token = os.getenv("COZE_API_TOKEN")
    workflow_id = os.getenv("COZE_WORKFLOW_ID")
    
    if not coze_token or not workflow_id:
        raise ValueError("Missing COZE_API_TOKEN or COZE_WORKFLOW_ID environment variables")
    
    headers = {
        'Authorization': f'Bearer {coze_token}',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Host': 'api.coze.com',
        'Connection': 'keep-alive'
    }
    
    payload = {
        "workflow_id": workflow_id,
        "parameters": {
            "BOT_USER_INPUT": "",
            "timestamp": None,
            "link": url,
            "content": content or ""
        }
    }
    
    logger.info("调用 Coze API...")
    logger.info(f"Request payload: {json.dumps(payload, ensure_ascii=False)}")
    
    response = requests.post(coze_api_url, headers=headers, json=payload)
    response.raise_for_status()
    
    result = response.json()
    logger.info(f"Coze API 响应: {json.dumps(result, ensure_ascii=False)}")
    
    return result

def handle_request_processing(request_id: int, url: str, content: str) -> None:
    """处理请求的具体逻辑"""
    try:
        logger.info(f"开始处理请求 ID: {request_id}")
        
        # 调用 Coze API
        result = call_coze_api(url, content)
        
        # 更新数据库
        supabase = get_supabase_client()
        data = supabase.table('keep_article_requests').update({
            'status': 'processed',
            'parsed_content': json.dumps(result, ensure_ascii=False)  # 保存解析结果
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
        handle_request_processing(request_id, url, content)
        
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