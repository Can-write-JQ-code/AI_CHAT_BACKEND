"""
应用配置模块
负责加载和管理所有环境变量配置
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import List

# 加载环境变量（支持从仓库根目录运行）
load_dotenv()
backend_env = Path(__file__).resolve().parent / ".env"
if backend_env.exists():
    load_dotenv(backend_env, override=True)


class Config:
    """应用配置类"""

    # 应用基础配置
    APP_TITLE = "AI Image Generation API"
    APP_VERSION = "1.0.0"

    # CORS 配置
    ALLOWED_ORIGINS_STR = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5500,http://localhost:5500"
    )

    @classmethod
    def get_allowed_origins(cls) -> List[str]:
        """获取允许的 CORS 源列表"""
        origins = cls.ALLOWED_ORIGINS_STR.split(",")
        if len(origins) == 1 and origins[0] == "*":
            return ["*"]
        return [origin.strip() for origin in origins if origin.strip()]

    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY")
    CHAT_API_KEY = os.getenv("CHAT_API_KEY")
    MIMO_API_KEY = os.getenv("MIMO_API_KEY")

    # Gemini 配置
    GEMINI_BASE_URL = os.getenv("GEMINI_BASE_URL", "https://yunwu.ai")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-image")
    GEMINI_AUTH_MODE = os.getenv("GEMINI_AUTH_MODE")

    # Doubao 配置
    DOUBAO_BASE_URL = os.getenv("DOUBAO_BASE_URL", "https://yunwu.ai")
    DOUBAO_MODEL = os.getenv("DOUBAO_MODEL", "doubao-seedream-4-0-250828")

    # Chat 配置
    CHAT_BASE_URL = os.getenv("CHAT_BASE_URL", "https://yunwu.ai/v1")
    CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-5.2-2025-12-11")

    # MiMO 配置
    MIMO_BASE_URL = os.getenv("MIMO_BASE_URL", "https://api.xiaomimimo.com/v1")
    MIMO_MODEL = os.getenv("MIMO_MODEL", "mimo-v2-flash")
    MIMO_TEMPERATURE = float(os.getenv("MIMO_TEMPERATURE", "0.8"))
    MIMO_TOP_P = float(os.getenv("MIMO_TOP_P", "0.95"))
    MIMO_MAX_TOKENS = int(os.getenv("MIMO_MAX_TOKENS", "1024"))

    # Sora 视频配置
    SORA_API_KEY = os.getenv("SORA_API_KEY") or os.getenv("OPENAI_API_KEY")
    SORA_BASE_URL = os.getenv("SORA_BASE_URL", "https://yunwu.ai/v1")
    SORA_DEFAULT_ORIENTATION = os.getenv("SORA_DEFAULT_ORIENTATION", "landscape")
    SORA_DEFAULT_DURATION = int(os.getenv("SORA_DEFAULT_DURATION", "15"))

    # VEO 视频配置
    VEO_API_KEY = os.getenv("VEO_API_KEY") or GEMINI_API_KEY
    VEO_BASE_URL = os.getenv("VEO_BASE_URL", "https://yunwu.ai")
    VEO_MODEL = os.getenv("VEO_MODEL", "veo3-fast")
    VEO_DEFAULT_ASPECT_RATIO = os.getenv("VEO_DEFAULT_ASPECT_RATIO", "16:9")
    VEO_ENHANCE_PROMPT = os.getenv("VEO_ENHANCE_PROMPT", "true").lower() == "true"
    VEO_UPSAMPLE = os.getenv("VEO_UPSAMPLE", "true").lower() == "true"

    # 视频上传配置
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_VIDEO_SIZE = int(os.getenv("MAX_VIDEO_SIZE", str(100 * 1024 * 1024)))  # 100MB

    @classmethod
    def print_debug_info(cls):
        """打印配置调试信息"""
        print(f"[CONFIG] GEMINI_API_KEY: {'✓ Configured' if cls.GEMINI_API_KEY else '✗ Not configured'}")
        print(f"[CONFIG] DOUBAO_API_KEY: {'✓ Configured' if cls.DOUBAO_API_KEY else '✗ Not configured'}")
        print(f"[CONFIG] MIMO_API_KEY: {'✓ Configured' if cls.MIMO_API_KEY else '✗ Not configured'}")
        print(f"[CONFIG] OPENAI_API_KEY: {'✓ Configured' if cls.OPENAI_API_KEY else '✗ Not configured'}")
        print(f"[CONFIG] STABILITY_API_KEY: {'✓ Configured' if cls.STABILITY_API_KEY else '✗ Not configured'}")


# 打印配置信息
Config.print_debug_info()
