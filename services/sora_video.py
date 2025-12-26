import httpx
from typing import Dict, Any, Optional, List


class SoraVideoService:
    """Sora video generation service integration via yunwu.ai"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://yunwu.ai",
        model: str = "sora-2"
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.create_endpoint = f"{self.base_url}/v1/video/create"
        self.query_endpoint = f"{self.base_url}/v1/video/query"

    async def create_video(
        self,
        prompt: str,
        orientation: str = "landscape",
        duration: int = 15,
        watermark: bool = False,
        private: bool = True,
        images: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a video generation task.
        
        Args:
            prompt: Text description for video generation
            orientation: 'portrait' (竖屏) or 'landscape' (横屏)
            duration: Video duration in seconds (15 or 25)
            watermark: Whether to add watermark
            private: Whether to keep video private
            images: Optional list of reference image URLs for image-to-video
            
        Returns:
            Dict with task_id and status, or error information
        """
        if not self.api_key:
            return {
                "success": False,
                "message": "Sora API key not configured"
            }

        # Validate parameters
        if orientation not in ("portrait", "landscape"):
            orientation = "landscape"
        if duration not in (15, 25):
            duration = 15

        payload = {
            "model": self.model,
            "prompt": prompt,
            "orientation": orientation,
            "size": "large",  # 1080p
            "duration": duration,
            "watermark": watermark,
            "private": private,
            "images": images or []
        }

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
                    "message": f"Sora API error: {response.status_code} - {response.text}"
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
                "message": "视频生成任务已创建",
                "metadata": {
                    "model": self.model,
                    "orientation": orientation,
                    "duration": duration,
                    "prompt": prompt
                }
            }

        except httpx.TimeoutException:
            return {
                "success": False,
                "message": "Sora request timed out. Please try again."
            }
        except Exception as exc:
            return {
                "success": False,
                "message": f"Sora video creation failed: {str(exc)}"
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
                "message": "Sora API key not configured"
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
                    "message": f"Sora API error: {response.status_code} - {response.text}"
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
                result["message"] = "视频生成完成"
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
        return f"Sora Video ({self.model})"
