"""
Pixel Alchemist - 像素动画生成器
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .api.routes import router
from .config import settings

# 创建 FastAPI 应用
app = FastAPI(
    title="Pixel Alchemist",
    description="像素动画精灵图生成器 - 上传参考图，输入动作描述，AI 生成像素动画",
    version="0.1.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api")

# 静态文件服务 (输出目录)
output_dir = Path(settings.output_dir)
output_dir.mkdir(parents=True, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=str(output_dir)), name="outputs")


@app.get("/")
async def root():
    """根路径 - API 信息"""
    return {
        "name": "Pixel Alchemist",
        "version": "0.1.0",
        "description": "像素动画精灵图生成器",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
