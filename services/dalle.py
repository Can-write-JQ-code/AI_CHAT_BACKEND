import httpx
from typing import Dict, Any, Optional
from .base import AIServiceBase


class DalleService(AIServiceBase):
    """DALL-E image generation service integration"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.base_url = "https://api.openai.com/v1/images/generations"
    
    async def generate_image(
        self, 
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        n: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate image using DALL-E 3
        
        Args:
            prompt: Image description
            size: Image size (1024x1024, 1792x1024, 1024x1792)
            quality: Image quality (standard, hd)
            n: Number of images to generate
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "DALL-E API key not configured"
            }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "dall-e-3",
                        "prompt": prompt,
                        "size": size,
                        "quality": quality,
                        "n": n
                    },
                    timeout=180.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "image_url": data["data"][0]["url"],
                        "metadata": {
                            "revised_prompt": data["data"][0].get("revised_prompt"),
                            "size": size,
                            "quality": quality
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": f"DALL-E API error: {response.status_code} - {response.text}"
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"DALL-E generation failed: {str(e)}"
            }
    
    def get_service_name(self) -> str:
        return "DALL-E 3"
