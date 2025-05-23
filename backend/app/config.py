from pydantic_settings import BaseSettings
from typing import Optional, List
from app.utils.logger import logger
import os

class Settings(BaseSettings):

    # 日志配置
    log_level: str 

    # Supabase 配置
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    
    # Webshare 配置
    WEBSHARE_API_TOKEN: str
    
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
    COZE_FILE_SUMMARY_ID_ZH: str  # 中文文件工作流
    COZE_FILE_SUMMARY_ID_EN: str  # 英文文件工作流

    # 是否使用mock coze
    USE_MOCK_COZE: bool = False
    
    # AssemblyAI 配置
    ASSEMBLYAI_API_KEY: str

    # Deepseek 配置
    DEEPSEEK_API_KEY: str

    # OpenRouter Configuration
    OPENROUTER_API_KEY: str
    
    # Bedrock Configuration
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str

    # 代理配置
    USE_PROXY: bool = False
    PROXY_URL: Optional[str] = None
    
    # CORS 配置
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://47.116.210.164:8000",
        "https://keep-up-nine.vercel.app"
    ]
    
    # 代理测试配置
    PROXY_LIST: str = ""  # 改为 str 类型
    PROXY_TEST_TIMEOUT: int = 10
    PROXY_TEST_MAX_WORKERS: int = 5
    YOUTUBE_TEST_URL: str = "https://www.youtube.com/watch?v=IFvLorAL5-8"
    
    @property
    def proxy_list(self) -> List[str]:
        """将代理字符串转换为列表"""
        if not self.PROXY_LIST:
            return []
        return [x.strip() for x in self.PROXY_LIST.split(',') if x.strip()]
    
    class Config:
        env_file = ".env"
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 确保 USE_PROXY 是布尔值
        if isinstance(self.USE_PROXY, str):
            self.USE_PROXY = self.USE_PROXY.lower() == 'true'
        logger.info(f"代理配置 - USE_PROXY: {self.USE_PROXY}, PROXY_URL: {self.PROXY_URL}")

settings = Settings() 