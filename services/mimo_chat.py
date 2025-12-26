import httpx
from typing import List, Dict, Any, Optional


class MimoChatService:
    """Xiaomi MiMO chat service (OpenAI-compatible)"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.xiaomimimo.com/v1",
        model: str = "mimo-v2-flash",
        temperature: float = 0.8,
        top_p: float = 0.95,
        max_completion_tokens: int = 1024,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.max_completion_tokens = max_completion_tokens
        self.endpoint = f"{self.base_url}/chat/completions"

    async def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not self.api_key:
            return {
                "success": False,
                "message": "MiMO API key not configured",
            }

        payload: Dict[str, Any] = {
            "model": model or self.model,
            "messages": messages,
            "max_completion_tokens": self.max_completion_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "stream": False,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "extra_body": {"thinking": {"type": "disabled"}},
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.endpoint,
                    headers=headers,
                    json=payload,
                    timeout=180.0,
                )

            if response.status_code == 200:
                data = response.json()
                content = (
                    data.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                )
                return {
                    "success": True,
                    "message": content,
                    "data": data,
                }

            return {
                "success": False,
                "message": f"MiMO API error: {response.status_code} - {response.text}",
            }

        except httpx.TimeoutException:
            return {
                "success": False,
                "message": "MiMO request timed out",
            }
        except Exception as exc:
            return {
                "success": False,
                "message": f"MiMO request failed: {str(exc)}",
            }

    def get_service_name(self) -> str:
        return f"小米 MiMO Chat ({self.model})"
