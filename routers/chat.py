"""
聊天路由
处理文本聊天相关的 API 端点
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from dependencies import chat_service, mimo_chat_service, history_manager

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    messages: List[Dict[str, Any]]
    service: str = "chat"
    model: Optional[str] = None


@router.post("/text_chat")
async def text_chat(request: ChatRequest):
    """
    处理文本/多模态聊天请求
    """
    try:
        print(f"[DEBUG] Chat request - Service: {request.service}, Messages: {len(request.messages)}")

        # 根据服务选择聊天提供商
        if request.service == "mimo-chat":
            chat_provider = mimo_chat_service
        elif request.service in (None, "chat"):
            chat_provider = chat_service
        else:
            return {
                "success": False,
                "message": f"Unsupported chat service: {request.service}"
            }

        result = await chat_provider.chat_completion(
            messages=request.messages,
            model=request.model
        )

        if result["success"]:
            # 保存到历史记录
            last_user_msg = next((m for m in reversed(request.messages) if m["role"] == "user"), None)
            prompt_text = last_user_msg["content"] if last_user_msg else "Unknown"

            # 如果内容是列表（多模态），提取文本
            if isinstance(prompt_text, list):
                text_part = next((p["text"] for p in prompt_text if p["type"] == "text"), "")
                prompt_text = text_part

            history_manager.add_history(
                type="chat",
                prompt=str(prompt_text),
                response=result["message"],
                metadata={
                    "model": request.model or chat_provider.model,
                    "service": request.service
                }
            )

        return result

    except Exception as e:
        print(f"[ERROR] Chat failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
