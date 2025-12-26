from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class AIServiceBase(ABC):
    """Base class for AI image generation services"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    @abstractmethod
    async def generate_image(
        self, 
        prompt: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate an image based on the prompt
        
        Args:
            prompt: Text description of the image to generate
            **kwargs: Additional service-specific parameters
            
        Returns:
            Dict containing:
                - success: bool
                - image_url: str (if successful)
                - error: str (if failed)
                - metadata: dict (optional)
        """
        pass
    
    @abstractmethod
    def get_service_name(self) -> str:
        """Return the name of the AI service"""
        pass
