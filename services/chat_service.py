import httpx
from typing import List, Dict, Any, Optional
import os
import json

class ChatService:
    """
    Chat Service integration (OpenAI-compatible)
    Supports text and multimodal (image) chat.
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        base_url: str = "https://yunwu.ai/v1",
        model: str = "gpt-5.1-2025-11-13"
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        
    async def chat_completion(
        self, 
        messages: List[Dict[str, Any]],
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send chat completion request
        
        Args:
            messages: List of message objects [{"role": "user", "content": ...}]
            model: Optional model override
            
        Returns:
            Dict with success status and response content
        """
        if not self.api_key:
            return {
                "success": False,
                "message": "API key not configured"
            }
            
        target_model = model or self.model
        endpoint = f"{self.base_url}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": target_model,
            "messages": messages
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint,
                    headers=headers,
                    json=payload,
                    timeout=180.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    return {
                        "success": True,
                        "message": content,
                        "data": data
                    }
                else:
                    return {
                        "success": False,
                        "message": f"API Error: {response.status_code} - {response.text}"
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "message": f"Request failed: {str(e)}"
            }
