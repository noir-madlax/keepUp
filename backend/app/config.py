from pydantic_settings import BaseSettings
from typing import Optional
from app.utils.logger import logger
import os

class Settings(BaseSettings):

    # 日志配置
    log_level: str 

    # Supabase 配置
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    
    # Coze 配置
    COZE_API_TOKEN: str
    COZE_WORKFLOW_ID_ZH: str  # 中文工作流
    COZE_WORKFLOW_ID_EN: str  # 英文工作流
    COZE_POLISH_WORKFLOW_ID_ZH: str  # 中文润色工作流
    COZE_POLISH_WORKFLOW_ID_EN: str  # 英文润色工作流
    COZE_DETAILED_WORKFLOW_ID_ZH: str  # 中文分段详述工作流
    COZE_DETAILED_WORKFLOW_ID_EN: str  # 英文分段详述工作流
    COZE_WEB_SUMMARY_ID_ZH: str  # 中文网页工作流
    COZE_WEB_SUMMARY_ID_EN: str  # 英文网页工作流
    USE_MOCK_COZE: bool = False
    
    # AssemblyAI 配置
    ASSEMBLYAI_API_KEY: str
    
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