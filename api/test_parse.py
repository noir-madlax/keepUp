import os
from http.server import HTTPServer
from parse import handler
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CORSRequestHandler(handler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
        
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def run(server_class=HTTPServer, handler_class=CORSRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logger.info(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    # 设置环境变量
    os.environ['VITE_SUPABASE_URL'] = '你的_SUPABASE_URL'
    os.environ['VITE_SUPABASE_SERVICE_ROLE_KEY'] = '你的_SUPABASE_SERVICE_ROLE_KEY'
    
    run() 