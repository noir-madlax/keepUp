from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.services.proxy_tester import ProxyTester
from app.services.proxy_tester1 import ProxyTester1
from app.services.proxy_get import ProxyGetter
from app.config import settings
from app.utils.logger import logger
from typing import List

router = APIRouter()

async def test_proxies_background(proxies: List[str]):
    """后台执行代理测试"""
    try:
        tester = ProxyTester(
            proxies=proxies,
            timeout=settings.PROXY_TEST_TIMEOUT,
            test_url=settings.YOUTUBE_TEST_URL
        )
        await tester.run_tests()
    except Exception as e:
        logger.error(f"后台代理测试失败: {str(e)}", exc_info=True)

@router.post("/router/test")
async def test_proxies_endpoint(proxies: List[str], background_tasks: BackgroundTasks):
    """测试代理列表"""
    try:
        if not proxies:
            raise HTTPException(status_code=400, detail="未提供代理列表")
        
        # 将测试任务添加到后台任务
        background_tasks.add_task(test_proxies_background, proxies)
        
        return {
            "status": "success",
            "message": f"已开始测试 {len(proxies)} 个代理",
            "total": len(proxies)
        }
        
    except Exception as e:
        logger.error(f"代理测试失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/router/get")
async def get_proxies():
    """从Webshare获取最新的代理列表"""
    try:
        getter = ProxyGetter()
        result = await getter.run()
        return result
        
    except Exception as e:
        logger.error(f"获取代理列表失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/router/proxy_tester_db")
async def proxy_tester_db():
    """测试数据库中的所有代理"""
    try:
        tester = ProxyTester1(
            timeout=settings.PROXY_TEST_TIMEOUT,
            test_url=settings.YOUTUBE_TEST_URL
        )
        
        results = await tester.run_tests(max_workers=20)
        return results
        
    except Exception as e:
        logger.error(f"代理测试失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 