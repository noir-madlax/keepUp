from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Supabase 配置
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    
    # Coze 配置
    COZE_API_TOKEN: str
    COZE_WORKFLOW_ID: str
    
    # CORS 配置
    CORS_ORIGINS: list[str] = [
        "http://localhost:8000",
        "http://47.116.210.164:8000",
        "https://*.vercel.app",
        "https://*.now.sh"
    ]
    
    class Config:
        env_file = ".env"

settings = Settings() 