"""
依赖注入模块
负责初始化和管理所有服务实例
"""
from services.dalle import DalleService
from services.stable_diffusion import StableDiffusionService
from services.gemini_image import GeminiImageService
from services.doubao_image import DoubaoImageService
from services.chat_service import ChatService
from services.sora_video import SoraVideoService
from services.veo_video import VeoVideoService
from services.mimo_chat import MimoChatService
from services.video_upload import VideoUploadService
from services.video_analysis import VideoAnalysisService
from history import HistoryManager
from config import Config


# 图片生成服务
dalle_service = DalleService(api_key=Config.OPENAI_API_KEY)

sd_service = StableDiffusionService(api_key=Config.STABILITY_API_KEY)

gemini_service = GeminiImageService(
    api_key=Config.GEMINI_API_KEY,
    base_url=Config.GEMINI_BASE_URL,
    model=Config.GEMINI_MODEL,
    auth_mode=Config.GEMINI_AUTH_MODE
)

doubao_service = DoubaoImageService(
    api_key=Config.DOUBAO_API_KEY,
    base_url=Config.DOUBAO_BASE_URL,
    model=Config.DOUBAO_MODEL
)

# 聊天服务
chat_service = ChatService(
    api_key=Config.CHAT_API_KEY or Config.GEMINI_API_KEY or Config.OPENAI_API_KEY,
    base_url=Config.CHAT_BASE_URL,
    model=Config.CHAT_MODEL
)

mimo_chat_service = MimoChatService(
    api_key=Config.MIMO_API_KEY,
    base_url=Config.MIMO_BASE_URL,
    model=Config.MIMO_MODEL,
    temperature=Config.MIMO_TEMPERATURE,
    top_p=Config.MIMO_TOP_P,
    max_completion_tokens=Config.MIMO_MAX_TOKENS
)

# 视频服务
sora_service = SoraVideoService(
    api_key=Config.SORA_API_KEY,
    base_url=Config.SORA_BASE_URL
)

veo_service = VeoVideoService(
    api_key=Config.VEO_API_KEY,
    base_url=Config.VEO_BASE_URL,
    model=Config.VEO_MODEL
)

video_upload_service = VideoUploadService(
    upload_dir=Config.UPLOAD_DIR
)

video_analysis_service = VideoAnalysisService(
    api_key=Config.GEMINI_API_KEY,
    base_url=Config.GEMINI_BASE_URL,
    model="gemini-2.5-pro"
)

# 历史记录管理器
history_manager = HistoryManager()


def get_image_service(service_name: str):
    """根据服务名称获取对应的图片生成服务"""
    services = {
        'dalle': dalle_service,
        'stable-diffusion': sd_service,
        'gemini-image': gemini_service,
        'doubao-image': doubao_service,
    }
    return services.get(service_name)


def get_chat_service(service_name: str):
    """根据服务名称获取对应的聊天服务"""
    services = {
        'chat': chat_service,
        'mimo-chat': mimo_chat_service,
    }
    return services.get(service_name)


def get_video_service(service_name: str):
    """根据服务名称获取对应的视频生成服务"""
    services = {
        'sora-video': sora_service,
        'veo-video': veo_service,
    }
    return services.get(service_name)
