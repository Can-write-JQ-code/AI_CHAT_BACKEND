"""
Pydantic 数据模型
定义所有 API 请求和响应的数据结构
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


# ============ 图片生成相关模型 ============

class ImageGenerationRequest(BaseModel):
    """图片生成请求"""
    prompt: str
    service: str = 'gemini-image'
    aspect_ratio: Optional[str] = '1:1'
    image_size: Optional[str] = '1K'
    model: Optional[str] = None
    image_data: Optional[str] = None  # Base64 编码的图片数据


class ImageGenerationResponse(BaseModel):
    """图片生成响应"""
    success: bool
    image_url: Optional[str] = None
    message: str
    metadata: Optional[Dict[str, Any]] = None


# ============ 聊天相关模型 ============

class ChatRequest(BaseModel):
    """聊天请求"""
    message: str
    service: str = 'chat'
    image_data: Optional[str] = None


class ChatResponse(BaseModel):
    """聊天响应"""
    success: bool
    message: str
    reply: Optional[str] = None


# ============ 视频生成相关模型 ============

class VideoGenerationRequest(BaseModel):
    """Sora 视频生成请求"""
    prompt: str
    orientation: Optional[str] = 'landscape'
    duration: Optional[int] = 15
    image_data: Optional[str] = None


class VeoVideoGenerationRequest(BaseModel):
    """VEO 视频生成请求"""
    prompt: str
    model: Optional[str] = 'veo3-fast'
    aspect_ratio: Optional[str] = '16:9'
    enhance_prompt: Optional[bool] = True
    upsample: Optional[bool] = True
    image_data: Optional[str] = None  # 单张图片（兼容旧格式）
    images: Optional[List[str]] = None  # 多张图片数组（新格式）


class VideoGenerationResponse(BaseModel):
    """视频生成响应"""
    success: bool
    video_url: Optional[str] = None
    message: str
    metadata: Optional[Dict[str, Any]] = None


# ============ 视频分析相关模型 ============

class VideoAnalysisResponse(BaseModel):
    """视频分析响应"""
    success: bool
    analysis: Optional[str] = None
    message: str
    metadata: Optional[Dict[str, Any]] = None


class VideoListResponse(BaseModel):
    """视频列表响应"""
    count: int
    videos: List[Dict[str, Any]]


# ============ 历史记录相关模型 ============

class HistoryItem(BaseModel):
    """历史记录项"""
    id: int
    prompt: str
    result_url: Optional[str] = None
    service: str
    created_at: str


class HistoryResponse(BaseModel):
    """历史记录响应"""
    items: List[HistoryItem]


# ============ 服务状态相关模型 ============

class ServiceInfo(BaseModel):
    """服务信息"""
    id: str
    name: str
    available: bool


class ServicesResponse(BaseModel):
    """服务列表响应"""
    services: List[ServiceInfo]
