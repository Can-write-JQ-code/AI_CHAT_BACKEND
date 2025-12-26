"""
AI 图片生成 API 主应用
重构版本 - 模块化架构
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import Config
from models import ServiceInfo, ServicesResponse
from dependencies import (
    dalle_service,
    sd_service,
    gemini_service,
    doubao_service,
    chat_service,
    mimo_chat_service,
    sora_service,
    veo_service,
    video_analysis_service,
)

# 导入所有路由
from routers import image, chat, video, video_analysis, history

# 创建 FastAPI 应用
app = FastAPI(
    title=Config.APP_TITLE,
    version=Config.APP_VERSION,
    description="AI 图片、视频生成和分析 API"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(image.router)
app.include_router(chat.router)
app.include_router(video.router)
app.include_router(video_analysis.router)
app.include_router(history.router)


@app.get("/")
async def root():
    """
    API 健康检查
    """
    return {
        "status": "online",
        "message": "AI Image Generation API",
        "version": Config.APP_VERSION,
        "available_services": [
            "dalle", "stable-diffusion", "gemini-image", "doubao-image",
            "chat", "mimo-chat",
            "sora-video", "veo-video",
            "video-analysis"
        ]
    }


@app.get("/api/services", response_model=ServicesResponse)
async def get_services():
    """
    获取可用的 AI 服务列表
    """
    services_list = [
        # 图片生成服务
        ServiceInfo(
            id="dalle",
            name=dalle_service.get_service_name(),
            available=dalle_service.api_key is not None
        ),
        ServiceInfo(
            id="stable-diffusion",
            name=sd_service.get_service_name(),
            available=sd_service.api_key is not None
        ),
        ServiceInfo(
            id="gemini-image",
            name=gemini_service.get_service_name(),
            available=gemini_service.api_key is not None
        ),
        ServiceInfo(
            id="doubao-image",
            name=doubao_service.get_service_name(),
            available=doubao_service.api_key is not None
        ),

        # 聊天服务
        ServiceInfo(
            id="chat",
            name="AI Chat (GPT-5.2)",
            available=chat_service.api_key is not None
        ),
        ServiceInfo(
            id="mimo-chat",
            name=mimo_chat_service.get_service_name(),
            available=mimo_chat_service.api_key is not None
        ),

        # 视频服务
        ServiceInfo(
            id="sora-video",
            name="Sora 视频生成",
            available=sora_service.api_key is not None
        ),
        ServiceInfo(
            id="veo-video",
            name="VEO 视频生成 (Google)",
            available=veo_service.api_key is not None
        ),

        # 视频分析服务
        ServiceInfo(
            id="video-analysis",
            name="Gemini 2.5 Pro 视频分析",
            available=video_analysis_service.api_key is not None
        ),
    ]

    return ServicesResponse(services=services_list)


@app.get("/health")
async def health_check():
    """
    健康检查端点
    """
    return {
        "status": "healthy",
        "version": Config.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
