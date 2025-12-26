import httpx
from typing import Dict, Any, Optional
from .base import AIServiceBase


class StableDiffusionService(AIServiceBase):
    """Stable Diffusion image generation service (via Stability AI API)"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.base_url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
    
    async def generate_image(
        self, 
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        steps: int = 30,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate image using Stable Diffusion XL
        
        Args:
            prompt: Image description
            width: Image width (must be multiple of 64)
            height: Image height (must be multiple of 64)
            steps: Number of diffusion steps
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "Stability AI API key not configured"
            }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    json={
                        "text_prompts": [
                            {
                                "text": prompt,
                                "weight": 1
                            }
                        ],
                        "cfg_scale": 7,
                        "height": height,
                        "width": width,
                        "steps": steps,
                        "samples": 1
                    },
                    timeout=180.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Note: Stability AI returns base64 encoded images
                    # You may need to save and serve them
                    return {
                        "success": True,
                        "image_data": data["artifacts"][0]["base64"],
                        "metadata": {
                            "width": width,
                            "height": height,
                            "steps": steps,
                            "seed": data["artifacts"][0].get("seed")
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Stability AI error: {response.status_code} - {response.text}"
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Stable Diffusion generation failed: {str(e)}"
            }
    
    def get_service_name(self) -> str:
        return "Stable Diffusion XL"
