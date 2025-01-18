from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.parse import router as parse_router
from app.routers.fetch import router as fetch_router
from app.routers.workflow import router as workflow_router
from app.config import settings
from app.routers import chat
from app.routers import article_views

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
app.include_router(parse_router)
app.include_router(fetch_router)
app.include_router(workflow_router)
app.include_router(chat.router)
app.include_router(article_views.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 