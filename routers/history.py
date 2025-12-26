"""
历史记录路由
处理历史记录相关的 API 端点
"""
from fastapi import APIRouter, HTTPException

from models import HistoryResponse
from dependencies import history_manager

router = APIRouter(prefix="/api", tags=["history"])


@router.get("/history", response_model=dict)
async def get_history():
    """
    获取聊天历史记录
    """
    try:
        history = history_manager.get_history()
        return {
            "success": True,
            "history": history
        }

    except Exception as e:
        print(f"[ERROR] Failed to get history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve history")


@router.delete("/history/{item_id}")
async def delete_history_item(item_id: int):
    """
    删除特定的历史记录项
    """
    try:
        success = history_manager.delete_history(item_id)

        if success:
            return {
                "success": True,
                "message": "History item deleted"
            }
        else:
            raise HTTPException(status_code=404, detail="History item not found")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history")
async def clear_history():
    """
    清空所有历史记录
    """
    try:
        history_manager.clear_history()
        return {
            "success": True,
            "message": "History cleared"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
