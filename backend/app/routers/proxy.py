from fastapi import APIRouter, HTTPException
from app.services.proxy_tester import ProxyTester
from app.config import settings
from app.utils.logger import logger

router = APIRouter()

@router.post("/router/test")
async def test_proxies():
    """测试所有配置的代理"""
    try:
        proxy_list = settings.proxy_list
        if not proxy_list:
            raise HTTPException(status_code=400, detail="未配置代理列表")
            
        tester = ProxyTester(
            proxies=proxy_list,
            timeout=settings.PROXY_TEST_TIMEOUT,
            test_url=settings.YOUTUBE_TEST_URL
        )
        
        results = await tester.run_tests()
        return results
        
    except Exception as e:
        logger.error(f"代理测试失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 