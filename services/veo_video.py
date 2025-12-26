import httpx
from typing import Dict, Any, Optional, List


class VeoVideoService:
    """VEO video generation service integration via yunwu.ai"""

    # Available VEO models
    MODELS = [
        "veo2", "veo2-fast", "veo2-fast-frames", "veo2-fast-components", "veo2-pro",
        "veo3", "veo3-fast", "veo3-pro", "veo3-pro-frames", "veo3-fast-frames", "veo3-frames"
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://yunwu.ai",
        model: str = "veo3-fast"
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.create_endpoint = f"{self.base_url}/v1/video/create"
        self.query_endpoint = f"{self.base_url}/v1/video/query"

    async def create_video(
        self,
        prompt: str,
        model: Optional[str] = None,
        aspect_ratio: str = "16:9",
        enhance_prompt: bool = True,
        enable_upsample: bool = True,
        images: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a video generation task using VEO.
        
        Args:
            prompt: Text description for video generation
            model: VEO model variant (veo2, veo3, veo3-fast, etc.)
            aspect_ratio: "16:9" or "9:16" (only for veo3)
            enhance_prompt: Auto-translate Chinese to English
            enable_upsample: Enable super-resolution
            images: Reference images for frames models
            
        Returns:
            Dict with task_id and status, or error information
        """
        if not self.api_key:
            return {
                "success": False,
                "message": "VEO API key not configured"
            }

        use_model = model or self.model
        
        # Validate aspect ratio
        if aspect_ratio not in ("16:9", "9:16"):
            aspect_ratio = "16:9"

        payload = {
            "model": use_model,
            "prompt": prompt,
            "enhance_prompt": enhance_prompt,
            "enable_upsample": enable_upsample,
            "aspect_ratio": aspect_ratio
        }
        
        # Add images if provided (for frames/components models)
        if images:
            payload["images"] = images

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.create_endpoint,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    json=payload,
                    timeout=180.0
                )

            if response.status_code != 200:
                return {
                    "success": False,
                    "message": f"VEO API error: {response.status_code} - {response.text}"
                }

            data = response.json()
            
            # Extract task ID from response
            task_id = data.get("id")
            status = data.get("status", "pending")
            
            if not task_id:
                return {
                    "success": False,
                    "message": "No task ID returned from API",
                    "raw_response": data
                }

            return {
                "success": True,
                "task_id": task_id,
                "status": status,
                "message": "VEO 视频生成任务已创建",
                "metadata": {
                    "model": use_model,
                    "aspect_ratio": aspect_ratio,
                    "enhance_prompt": enhance_prompt,
                    "prompt": prompt
                }
            }

        except httpx.TimeoutException:
            return {
                "success": False,
                "message": "VEO request timed out. Please try again."
            }
        except Exception as exc:
            return {
                "success": False,
                "message": f"VEO video creation failed: {str(exc)}"
            }

    async def query_video(self, task_id: str) -> Dict[str, Any]:
        """
        Query the status of a video generation task.
        
        Args:
            task_id: The task ID returned from create_video
            
        Returns:
            Dict with status, video_url (if completed), and other metadata
        """
        if not self.api_key:
            return {
                "success": False,
                "message": "VEO API key not configured"
            }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.query_endpoint,
                    params={"id": task_id},
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    timeout=180.0
                )

            if response.status_code != 200:
                return {
                    "success": False,
                    "message": f"VEO API error: {response.status_code} - {response.text}"
                }

            data = response.json()
            
            status = data.get("status", "unknown")
            video_url = data.get("video_url")
            enhanced_prompt = data.get("enhanced_prompt")
            
            result = {
                "success": True,
                "task_id": task_id,
                "status": status,
                "enhanced_prompt": enhanced_prompt
            }
            
            if status == "completed" and video_url:
                result["video_url"] = video_url
                result["message"] = "VEO 视频生成完成"
            elif status == "failed":
                result["success"] = False
                result["message"] = "视频生成失败"
            elif status == "pending":
                result["message"] = "视频正在排队中..."
            elif status == "processing":
                result["message"] = "视频正在生成中..."
            else:
                result["message"] = f"状态: {status}"

            return result

        except httpx.TimeoutException:
            return {
                "success": False,
                "message": "Query request timed out. Please try again."
            }
        except Exception as exc:
            return {
                "success": False,
                "message": f"Failed to query video status: {str(exc)}"
            }

    def get_service_name(self) -> str:
        return f"VEO Video ({self.model})"
