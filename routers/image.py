"""
图片生成路由
处理所有图片生成相关的 API 端点
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from PIL import Image
from io import BytesIO
import base64

from models import ImageGenerationRequest, ImageGenerationResponse
from dependencies import get_image_service, gemini_service, doubao_service, history_manager
from services.gemini_image import GeminiImageService
from services.doubao_image import DoubaoImageService
from config import Config

router = APIRouter(prefix="/api", tags=["images"])


from pydantic import BaseModel
from typing import Optional

class ImageChatRequest(BaseModel):
    service: str
    message: str
    model: Optional[str] = None
    aspect_ratio: str = "1:1"
    image_size: str = "1K"
    reference_image: Optional[str] = None


@router.post("/chat", response_model=dict)
async def generate_image_from_chat(request: ImageChatRequest):
    """
    生成图片（从聊天界面调用）
    """
    try:
        print(f"[DEBUG] Image generation - Service: {request.service}, Model: {request.model}")
        print(f"[DEBUG] Prompt: {request.message[:100]}...")
        print(f"[DEBUG] Aspect Ratio: {request.aspect_ratio}, Image Size: {request.image_size}")

        # 为 Gemini 和 Doubao 创建带特定模型的实例
        if request.service == "gemini-image":
            image_service = GeminiImageService(
                api_key=Config.GEMINI_API_KEY,
                base_url=Config.GEMINI_BASE_URL,
                model=request.model or Config.GEMINI_MODEL,
                auth_mode=Config.GEMINI_AUTH_MODE
            )
            kwargs = {
                "aspect_ratio": request.aspect_ratio,
                "image_size": request.image_size,
                "reference_image": request.reference_image
            }
        elif request.service == "doubao-image":
            image_service = DoubaoImageService(
                api_key=Config.DOUBAO_API_KEY,
                base_url=Config.DOUBAO_BASE_URL,
                model=request.model or Config.DOUBAO_MODEL
            )
            kwargs = {
                "aspect_ratio": request.aspect_ratio,
                "image_size": request.image_size,
                "reference_image": request.reference_image
            }
        else:
            image_service = get_image_service(request.service)
            kwargs = {}

        if not image_service:
            raise HTTPException(status_code=400, detail=f"Service '{request.service}' not found")

        # 生成图片
        result = await image_service.generate_image(prompt=request.message, **kwargs)

        if result["success"]:
            # 保存到历史记录
            history_manager.add_history(
                type="image",
                prompt=request.message,
                response=result.get("image_url") or "base64_image",
                metadata={
                    "service": request.service,
                    "model": request.model,
                    "aspect_ratio": request.aspect_ratio,
                    "image_size": request.image_size,
                    "image_data": result.get("image_data")
                }
            )

            return {
                "success": True,
                "message": result.get("message", "图片生成成功"),
                "image_url": result.get("image_url"),
                "image_data": result.get("image_data"),
                "metadata": result.get("metadata", {})
            }
        else:
            return {
                "success": False,
                "message": result.get("message", "Image generation failed")
            }

    except Exception as e:
        print(f"[ERROR] Image generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=dict)
async def generate_image_api(request: ImageGenerationRequest):
    """
    生成图片（通用 API 端点）
    """
    try:
        service_key = request.service

        # 获取服务实例
        if service_key == "gemini-image":
            service = GeminiImageService(
                api_key=Config.GEMINI_API_KEY,
                base_url=Config.GEMINI_BASE_URL,
                model=request.model or Config.GEMINI_MODEL,
                auth_mode=Config.GEMINI_AUTH_MODE
            )
            kwargs = {
                "aspect_ratio": request.aspect_ratio,
                "image_size": request.image_size,
                "reference_image": request.image_data
            }
        elif service_key == "doubao-image":
            service = DoubaoImageService(
                api_key=Config.DOUBAO_API_KEY,
                base_url=Config.DOUBAO_BASE_URL,
                model=request.model or Config.DOUBAO_MODEL
            )
            kwargs = {
                "aspect_ratio": request.aspect_ratio,
                "image_size": request.image_size,
                "reference_image": request.image_data
            }
        else:
            service = get_image_service(service_key)
            kwargs = {}

        if not service:
            raise HTTPException(status_code=400, detail=f"Service '{service_key}' not found")

        result = await service.generate_image(prompt=request.prompt, **kwargs)

        if result["success"]:
            return {
                "success": True,
                "image_url": result.get("image_url"),
                "image_data": result.get("image_data"),
                "metadata": result.get("metadata", {}),
                "service": request.service
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Image generation failed"))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    上传图片（用于图生图功能）
    """
    try:
        # 读取并验证图片
        contents = await file.read()
        image = Image.open(BytesIO(contents))

        # 转换为 base64 以便存储/处理
        buffered = BytesIO()
        image.save(buffered, format=image.format or "PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return {
            "success": True,
            "message": "Image uploaded successfully",
            "filename": file.filename,
            "size": len(contents),
            "format": image.format,
            "dimensions": f"{image.width}x{image.height}",
            "image_data": f"data:image/{(image.format or 'png').lower()};base64,{img_str}"
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
