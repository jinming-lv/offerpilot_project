from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api.resume import router as resume_router
from utils.logger import get_logger

logger = get_logger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="CareerPilot API",
    description="职业导航系统API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(resume_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "CareerPilot API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "app:app",  
        host="0.0.0.0",
        port=8000,
        reload=True
    )