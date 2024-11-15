import logging
import sys

# 创建日志记录器
logger = logging.getLogger("keepup")
logger.setLevel(logging.INFO)

# 创建控制台处理器
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# 创建格式化器
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 将格式化器添加到处理器
console_handler.setFormatter(formatter)

# 将处理器添加到记录器
logger.addHandler(console_handler)

# 确保日志不会被传播到父记录器
logger.propagate = False

# 添加一些辅助函数
def log_request_info(request_id: int, url: str):
    """记录请求信息"""
    logger.info(f"处理请求 - ID: {request_id}, URL: {url}")

def log_api_call(api_name: str):
    """记录 API 调用"""
    logger.info(f"调用 {api_name} API")

def log_error(error: Exception, context: str = None):
    """记录错误信息"""
    if context:
        logger.error(f"{context}: {str(error)}", exc_info=True)
    else:
        logger.error(str(error), exc_info=True) 