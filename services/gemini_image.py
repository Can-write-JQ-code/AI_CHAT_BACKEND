import httpx
from typing import Dict, Any, Optional, Tuple
from .base import AIServiceBase


class GeminiImageService(AIServiceBase):
    """Gemini Image Generation service integration (Official Google API)"""
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        base_url: str = "https://yunwu.ai",
        model: str = "gemini-2.5-flash-image",
        auth_mode: Optional[str] = None
    ):
        super().__init__(api_key)
        self.base_url = base_url
        self.model = model
        requested_mode = (auth_mode or "auto").strip().lower()
        if requested_mode not in {"auto", "x-goog", "bearer"}:
            requested_mode = "auto"
        if requested_mode == "auto":
            # Relay providers often issue OpenAI-style keys (sk- prefix) that
            # expect Authorization headers instead of x-goog headers.
            if self.api_key and self.api_key.startswith("sk-"):
                self.auth_mode = "bearer"
            else:
                self.auth_mode = "x-goog"
        else:
            self.auth_mode = requested_mode
        # Official endpoint format: /v1beta/models/{model}:generateContent
        self.endpoint = f"{base_url}/v1beta/models/{model}:generateContent"
    
    async def generate_image(
        self, 
        prompt: str,
        aspect_ratio: str = "1:1",
        image_size: str = "1K",
        reference_image: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate image using Gemini Image Generation API (Official)
        
        Args:
            prompt: Image description text
            aspect_ratio: Image aspect ratio (1:1, 16:9, 9:16, 4:3, 3:4, etc.)
            image_size: Image size (1K, 2K, 4K) - only for gemini-3-pro-image-preview
            reference_image: Optional base64 encoded reference image
        
        Returns:
            Dict with success status, image_data (base64), and metadata
        """
        if not self.api_key:
            return {
                "success": False,
                "message": "Gemini API key not configured"
            }
        
        try:
            # Build request parts - simple text prompt
            parts = [{"text": prompt}]
            
            # Add reference image if provided
            if reference_image:
                parts.append(self._prepare_reference_part(reference_image))
            
            # Build request body (simplified based on official docs)
            request_body = {
                "contents": [{
                    "parts": parts
                }]
            }
            
            # Add generation config for advanced model
            if "gemini-3-pro" in self.model:
                request_body["generationConfig"] = {
                    "responseModalities": ["TEXT", "IMAGE"],
                    "imageConfig": {
                        "aspectRatio": aspect_ratio,
                        "imageSize": image_size
                    }
                }
            
            headers = {
                "Content-Type": "application/json"
            }
            if self.auth_mode == "bearer":
                headers["Authorization"] = f"Bearer {self.api_key}"
            else:
                headers["x-goog-api-key"] = self.api_key
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.endpoint,
                    headers=headers,
                    json=request_body,
                    timeout=180.0  # Increased timeout to 180 seconds
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Parse response based on official API structure
                    try:
                        candidates = data.get("candidates", [])
                        if not candidates:
                            return {
                                "success": False,
                                "message": "No candidates in response"
                            }
                        
                        content = candidates[0].get("content", {})
                        parts = content.get("parts", [])
                        
                        # Extract image and text from parts
                        image_data = None
                        text_response = None
                        
                        image_mime = None
                        for part in parts:
                            # Check for inline_data (image)
                            if "inlineData" in part or "inline_data" in part:
                                inline = part.get("inlineData") or part.get("inline_data")
                                if inline:
                                    image_data = inline.get("data")
                                    image_mime = inline.get("mimeType") or inline.get("mime_type") or image_mime
                            # Check for text
                            elif "text" in part:
                                text_response = part["text"]
                        
                        if image_data:
                            return {
                                "success": True,
                                "image_data": image_data,
                                "text": text_response,
                                "message": f"图片生成成功 ({aspect_ratio}, {image_size})",
                                "metadata": {
                                    "aspect_ratio": aspect_ratio,
                                    "image_size": image_size,
                                    "model": self.model,
                                    "mime_type": image_mime or "image/png"
                                }
                            }
                        else:
                            return {
                                "success": False,
                                "message": "No image data in response",
                                "raw_response": data
                            }
                            
                    except (KeyError, IndexError) as e:
                        return {
                            "success": False,
                            "message": f"Failed to parse response: {str(e)}",
                            "raw_response": data
                        }
                else:
                    error_text = response.text
                    return {
                        "success": False,
                        "message": f"Gemini API error: {response.status_code} - {error_text}"
                    }
                    
        except httpx.TimeoutException:
            return {
                "success": False,
                "message": "Request timeout. Try using a lower resolution (1K or 2K)"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Gemini image generation failed: {str(e)}"
            }
    
    def get_service_name(self) -> str:
        return f"Gemini Image ({self.model})"

    def _prepare_reference_part(self, reference_image: str) -> Dict[str, Any]:
        mime_type, data = self._split_reference_image(reference_image)
        return {
            "inline_data": {
                "mime_type": mime_type,
                "data": data
            }
        }

    def _split_reference_image(self, reference_image: str) -> Tuple[str, str]:
        default_mime = "image/jpeg"
        if not reference_image:
            return default_mime, ""

        ref = reference_image.strip()
        if ref.startswith("data:"):
            try:
                header, base64_data = ref.split(",", 1)
                mime_type = header.split(";")[0].split(":")[1] or default_mime
                return mime_type, base64_data
            except ValueError:
                return default_mime, ref
        return default_mime, ref
