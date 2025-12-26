import httpx
from typing import Dict, Any, Optional, Union, List
from .base import AIServiceBase


class DoubaoImageService(AIServiceBase):
    """Doubao (Seedream 4.0) image generation service integration"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://yunwu.ai",
        model: str = "doubao-seedream-4-0-250828"
    ):
        super().__init__(api_key)
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.endpoint = f"{self.base_url}/v1/images/generations"

    async def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "1:1",
        image_size: str = "1K",
        reference_image: Optional[Union[str, List[str]]] = None,
        response_format: str = "b64_json",
        sequential_mode: str = "disabled",
        max_images: int = 1,
        watermark: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        if not self.api_key:
            return {
                "success": False,
                "message": "Doubao API key not configured"
            }

        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "response_format": response_format,
            "sequential_image_generation": sequential_mode,
            "watermark": watermark,
        }

        size_override = kwargs.get("size")
        payload["size"] = size_override or self._build_size(aspect_ratio, image_size)

        if sequential_mode == "auto":
            payload["sequential_image_generation_options"] = {
                "max_images": max(1, min(15, max_images))
            }

        if reference_image:
            formatted_image = self._format_image_input(reference_image)
            if formatted_image:
                payload["image"] = formatted_image

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.endpoint,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=180.0
                )

            if response.status_code != 200:
                return {
                    "success": False,
                    "message": f"Doubao API error: {response.status_code} - {response.text}"
                }

            data = response.json()
            images = data.get("data", [])
            if not images:
                return {
                    "success": False,
                    "message": "Doubao API returned no images",
                    "raw_response": data
                }

            first_image = images[0]
            image_data = first_image.get("b64_json")
            if image_data and isinstance(image_data, str):
                image_data = "".join(image_data.split())
            image_url = first_image.get("url")

            mime_type = first_image.get("mime_type") or "image/jpeg"

            if image_data:
                return {
                    "success": True,
                    "image_data": image_data,
                    "message": "豆包图片生成成功",
                    "metadata": {
                        "aspect_ratio": aspect_ratio,
                        "image_size": image_size,
                        "model": self.model,
                        "service": "doubao-image",
                        "mime_type": mime_type
                    }
                }
            elif image_url:
                return {
                    "success": True,
                    "image_url": image_url,
                    "message": "豆包图片生成成功（URL）",
                    "metadata": {
                        "aspect_ratio": aspect_ratio,
                        "image_size": image_size,
                        "model": self.model,
                        "service": "doubao-image",
                        "mime_type": mime_type
                    }
                }
            else:
                return {
                    "success": False,
                    "message": "Unknown response format",
                    "raw_response": data
                }

        except httpx.TimeoutException:
            return {
                "success": False,
                "message": "Doubao request timed out. Try a smaller size."
            }
        except Exception as exc:
            return {
                "success": False,
                "message": f"Doubao image generation failed: {str(exc)}"
            }

    def get_service_name(self) -> str:
        return f"Doubao Image ({self.model})"

    def _build_size(self, aspect_ratio: str, image_size: str) -> str:
        base_map = {
            "1K": 1024,
            "2K": 2048,
            "4K": 4096
        }
        base_value = base_map.get(image_size.upper(), 1024)
        width_ratio, height_ratio = self._parse_ratio(aspect_ratio)

        if width_ratio >= height_ratio:
            width = base_value
            height = max(512, int(round(base_value * height_ratio / max(width_ratio, 1))))
        else:
            height = base_value
            width = max(512, int(round(base_value * width_ratio / max(height_ratio, 1))))

        width = max(512, min(4096, width))
        height = max(512, min(4096, height))
        return f"{width}x{height}"

    def _parse_ratio(self, ratio: str) -> (int, int):
        try:
            parts = ratio.split(":")
            return max(1, int(parts[0])), max(1, int(parts[1]))
        except Exception:
            return 1, 1

    def _format_image_input(self, reference: Union[str, List[str]]) -> Union[str, List[str]]:
        if isinstance(reference, list):
            return [self._ensure_data_url(item) for item in reference if item]
        return self._ensure_data_url(reference)

    def _ensure_data_url(self, value: str) -> str:
        if not value:
            return value
        trimmed = value.strip()
        if trimmed.startswith("data:"):
            return trimmed
        return f"data:image/png;base64,{trimmed}"
