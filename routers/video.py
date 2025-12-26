"""
视频生成路由
处理 Sora 和 VEO 视频生成相关的 API 端点
"""
from fastapi import APIRouter, HTTPException

from models import VideoGenerationRequest, VeoVideoGenerationRequest, VideoGenerationResponse
from dependencies import sora_service, veo_service, history_manager

router = APIRouter(prefix="/api", tags=["video"])


@router.post("/video", response_model=dict)
async def generate_video_sora(request: VideoGenerationRequest):
    """
    生成 Sora 视频 (前端调用的端点)
    """
    return await generate_video(request)


@router.post("/generate_video", response_model=dict)
async def generate_video(request: VideoGenerationRequest):
    """
    生成 Sora 视频
    """
    try:
        print(f"[DEBUG] Sora video generation - Prompt: {request.prompt[:100]}...")
        print(f"[DEBUG] Orientation: {request.orientation}, Duration: {request.duration}")

        result = await sora_service.create_video(
            prompt=request.prompt,
            orientation=request.orientation,
            duration=request.duration,
            images=[request.image_data] if request.image_data else None
        )

        if result["success"]:
            # 保存到历史记录
            history_manager.add_history(
                type="video",
                prompt=request.prompt,
                response=result.get("video_url", "generated_video"),
                metadata={
                    "service": "sora-video",
                    "orientation": request.orientation,
                    "duration": request.duration
                }
            )

            return {
                "success": True,
                "video_url": result.get("video_url"),
                "message": result.get("message", "视频生成成功"),
                "metadata": result.get("metadata", {})
            }
        else:
            return {
                "success": False,
                "message": result.get("message", "视频生成失败")
            }

    except Exception as e:
        print(f"[ERROR] Sora video generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/veo_video", response_model=dict)
async def generate_veo_video(request: VeoVideoGenerationRequest):
    """
    生成 VEO 视频
    
    支持参考图片的模型：
    - veo3-fast-frames: 支持首帧参考（最多1张图片）
    - veo2-fast-frames: 支持首尾帧参考（最多2张图片）
    - veo2-fast-components: 支持多元素参考（最多3张图片）
    
    不支持参考图片的模型：
    - veo3, veo3-fast, veo3-pro, veo2, veo2-fast, veo2-pro
    """
    try:
        print(f"[DEBUG] VEO video generation - Model: {request.model}")
        print(f"[DEBUG] Prompt: {request.prompt[:100]}...")
        print(f"[DEBUG] Aspect Ratio: {request.aspect_ratio}")
        
        # 检查模型是否支持图片
        image_supported_models = ['veo3-fast-frames', 'veo2-fast-frames', 'veo2-fast-components']
        
        # 处理图片参数：支持 images 数组和 image_data 单张图片
        images = None
        has_images = False
        
        if request.images:
            # 新格式：images 数组
            images = request.images
            has_images = len(images) > 0
            print(f"[DEBUG] Using images array with {len(images)} images")
        elif request.image_data:
            # 旧格式：image_data 单张图片
            images = [request.image_data]
            has_images = True
            print(f"[DEBUG] Using single image_data")
        
        # 如果模型不支持图片，过滤掉图片参数
        if has_images and request.model not in image_supported_models:
            print(f"[WARNING] Model {request.model} does not support images, ignoring image data")
            images = None
            has_images = False
        
        # 根据模型限制图片数量
        if images and request.model in image_supported_models:
            if request.model == 'veo3-fast-frames':
                # 最多1张图片
                images = images[:1]
                print(f"[DEBUG] veo3-fast-frames: limited to 1 image")
            elif request.model == 'veo2-fast-frames':
                # 最多2张图片
                images = images[:2]
                print(f"[DEBUG] veo2-fast-frames: limited to 2 images")
            elif request.model == 'veo2-fast-components':
                # 最多3张图片
                images = images[:3]
                print(f"[DEBUG] veo2-fast-components: limited to 3 images")

        # 调用 VEO 服务的 create_video 方法
        result = await veo_service.create_video(
            prompt=request.prompt,
            model=request.model,
            aspect_ratio=request.aspect_ratio,
            enhance_prompt=request.enhance_prompt,
            enable_upsample=request.upsample,
            images=images
        )

        if result["success"]:
            # 保存到历史记录
            history_manager.add_history(
                type="video",
                prompt=request.prompt,
                response=result.get("task_id", "unknown_task"),
                metadata={
                    "service": "veo-video",
                    "model": request.model,
                    "aspect_ratio": request.aspect_ratio,
                    "task_id": result.get("task_id"),
                    "status": result.get("status"),
                    "has_images": has_images and request.model in image_supported_models
                }
            )

            return {
                "success": True,
                "task_id": result.get("task_id"),
                "status": result.get("status"),
                "message": result.get("message", "VEO 视频生成任务已创建"),
                "metadata": result.get("metadata", {})
            }
        else:
            return {
                "success": False,
                "message": result.get("message", "视频生成失败")
            }

    except Exception as e:
        print(f"[ERROR] VEO video generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate_veo_video", response_model=dict)
async def generate_veo_video_legacy(request: VeoVideoGenerationRequest):
    """
    生成 VEO 视频 (兼容旧端点)
    """
    return await generate_veo_video(request)


@router.get("/veo_video/{task_id}", response_model=dict)
async def get_veo_video_status(task_id: str):
    """
    查询 VEO 视频状态
    """
    try:
        result = await veo_service.query_video(task_id)
        
        if result["success"]:
            return {
                "success": True,
                "task_id": task_id,
                "status": result.get("status"),
                "video_url": result.get("video_url"),
                "message": result.get("message"),
                "metadata": {
                    "enhanced_prompt": result.get("enhanced_prompt")
                }
            }
        else:
            return {
                "success": False,
                "message": result.get("message", "查询失败")
            }

    except Exception as e:
        print(f"[ERROR] VEO video status query failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
