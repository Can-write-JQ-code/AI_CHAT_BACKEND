"""
视频分析路由
处理视频上传和分析相关的 API 端点
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pathlib import Path

from models import VideoAnalysisResponse, VideoListResponse
from dependencies import video_upload_service, video_analysis_service, history_manager

router = APIRouter(prefix="/api", tags=["video-analysis"])


@router.post("/video_analysis/upload", response_model=dict)
async def upload_and_analyze_video(
    file: UploadFile = File(...),
    prompt: str = Form("请用3句话总结这个视频的内容")
):
    """
    上传并分析视频
    """
    try:
        print(f"[DEBUG] Video analysis - Uploading: {file.filename}")

        # 保存视频文件
        upload_result = await video_upload_service.save_video(file)

        if not upload_result["success"]:
            return {
                "success": False,
                "message": upload_result["message"]
            }

        video_path = upload_result["file_path"]
        print(f"[DEBUG] Video saved to: {video_path}")

        # 分析视频
        print(f"[DEBUG] Analyzing video with prompt: {prompt}")
        analysis_result = await video_analysis_service.analyze_video(
            video_path=video_path,
            prompt=prompt
        )

        if analysis_result["success"]:
            # 保存到历史记录
            history_manager.add_history(
                type="video_analysis",
                prompt=prompt,
                response=analysis_result.get("analysis", ""),
                metadata={
                    "service": "video-analysis",
                    "video_filename": file.filename,
                    "video_path": video_path,
                    **analysis_result.get("metadata", {})
                }
            )

            return {
                "success": True,
                "analysis": analysis_result["analysis"],
                "message": analysis_result["message"],
                "metadata": analysis_result.get("metadata", {})
            }
        else:
            return {
                "success": False,
                "message": analysis_result["message"]
            }

    except Exception as e:
        print(f"[ERROR] Video analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/video_analysis/upload_multiple")
async def upload_multiple_videos(files: list[UploadFile] = File(...)):
    """
    上传多个视频文件
    """
    try:
        results = []
        for file in files:
            result = await video_upload_service.save_video(file)
            results.append(result)

        successful = sum(1 for r in results if r["success"])

        return {
            "success": True,
            "message": f"Successfully uploaded {successful}/{len(files)} videos",
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/videos", response_model=VideoListResponse)
async def list_videos():
    """
    获取已上传的视频列表
    """
    try:
        videos = video_upload_service.list_videos()
        return {
            "count": len(videos),
            "videos": videos
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/videos/{filename}")
async def get_video_info(filename: str):
    """
    获取特定视频的信息
    """
    try:
        video_info = video_upload_service.get_video_info(filename)

        if not video_info:
            raise HTTPException(status_code=404, detail="Video not found")

        return video_info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
