import asyncio
from app.utils.logger import logger
from functools import wraps
from typing import Type, Tuple

def retry_decorator(
    max_retries: int = 5,           # 最大重试次数
    base_delay: float = 1,          # 基础延迟时间(秒)
    max_delay: float = 30,          # 最大延迟时间(秒)
    exceptions: Tuple[Type[Exception], ...] = (Exception,)  # 需要重试的异常类型
):
    """
    异步函数重试装饰器
    
    Args:
        max_retries: 最大重试次数，默认3次
        base_delay: 基础延迟时间(秒)，默认2秒
        max_delay: 最大延迟时间(秒)，默认30秒
        exceptions: 需要重试的异常类型，默认所有异常
        
    Example:
        @retry_decorator(max_retries=3, exceptions=(httpx.TimeoutException,))
        async def my_function():
            # 异步操作
            pass
    """
    def decorator(func):
        # 使用闭包变量存储重试次数
        retry_count = {'value': 0}
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            while True:
                try:
                    # 更新闭包变量
                    retry_count['value'] = retries
                    return await func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(f"重试{max_retries}次后仍然失败: {str(e)}")
                        raise  # 重试次数用完后，重新抛出异常
                    
                    # 计算延迟时间（指数退避）
                    delay = min(base_delay * (2 ** (retries - 1)), max_delay)
                    
                    logger.warning(
                        f"操作失败，{delay}秒后进行第{retries}次重试。错误: {str(e)}"
                    )
                    
                    await asyncio.sleep(delay)
        
        # 添加获取重试次数的方法
        wrapper.get_retry_count = lambda: retry_count['value']
        return wrapper
    return decorator