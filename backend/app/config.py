from pydantic_settings import BaseSettings
from typing import Optional
from app.utils.logger import logger

class Settings(BaseSettings):
    # Supabase 配置
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    
    # Coze 配置
    COZE_API_TOKEN: str
    COZE_WORKFLOW_ID: str
    USE_MOCK_COZE: bool = False
    
    # 代理配置
    USE_PROXY: bool = False
    PROXY_URL: Optional[str] = None
    
    # CORS 配置
    CORS_ORIGINS: list[str] = [
        "http://localhost:8000",
        "http://47.116.210.164:8000",
        "https://*.vercel.app",
        "https://*.now.sh"
    ]
    
    class Config:
        env_file = ".env"
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 确保 USE_PROXY 是布尔值
        if isinstance(self.USE_PROXY, str):
            self.USE_PROXY = self.USE_PROXY.lower() == 'true'
        logger.info(f"代理配置 - USE_PROXY: {self.USE_PROXY}, PROXY_URL: {self.PROXY_URL}")

settings = Settings() 