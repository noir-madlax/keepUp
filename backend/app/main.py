from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import parse
from app.config import settings

app = FastAPI(title="Keep Up API")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(parse.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 