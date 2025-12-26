import http.client
import json
import base64
from typing import Dict, Any, Optional, List
from pathlib import Path
import os

class VideoAnalysisService:
    """视频分析服务 - 使用Gemini 2.5 Pro分析视频内容"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://yunwu.ai",
        model: str = "gemini-2.5-pro"
    ):
        """
        初始化视频分析服务

        Args:
            api_key: API密钥
            base_url: API基础URL (例如: https://yunwu.ai)
            model: 使用的模型名称
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.endpoint = f"/v1beta/models/{model}:generateContent"

        # 从 base_url 中提取主机名
        if self.base_url.startswith("https://"):
            self.host = self.base_url[8:]
        elif self.base_url.startswith("http://"):
            self.host = self.base_url[7:]
        else:
            self.host = self.base_url
        
    def _encode_video_to_base64(self, video_path: str) -> str:
        """
        将视频文件编码为base64字符串
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            base64编码的视频数据
        """
        try:
            with open(video_path, "rb") as video_file:
                video_data = video_file.read()
                return base64.b64encode(video_data).decode('utf-8')
        except Exception as e:
            raise Exception(f"视频文件读取失败: {str(e)}")
    
    async def analyze_video(
        self,
        video_path: str,
        prompt: str = "请用3句话总结这个视频的内容",
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        分析视频内容
        
        Args:
            video_path: 视频文件路径
            prompt: 分析提示词
            api_key: API密钥（可选，如果未在初始化时提供）
            
        Returns:
            分析结果
        """
        api_key = api_key or self.api_key
        
        if not api_key:
            return {
                "success": False,
                "message": "API密钥未配置"
            }
        
        try:
            # 验证视频文件存在
            if not Path(video_path).exists():
                return {
                    "success": False,
                    "message": f"视频文件不存在: {video_path}"
                }
            
            # 验证视频文件大小（限制为100MB）
            file_size = Path(video_path).stat().st_size
            max_size = 100 * 1024 * 1024  # 100MB
            if file_size > max_size:
                return {
                    "success": False,
                    "message": f"视频文件过大: {file_size / (1024*1024):.1f}MB / {max_size / (1024*1024):.0f}MB"
                }
            
            # 编码视频为base64
            video_base64 = self._encode_video_to_base64(video_path)

            # 构建请求体
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {
                                "inline_data": {
                                    "mime_type": "video/mp4",
                                    "data": video_base64
                                }
                            },
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            }

            # 发送请求（视频分析需要更长的超时时间）
            # 超时设置为180秒（3分钟）
            conn = http.client.HTTPSConnection(self.host, timeout=180)
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }

            # 根据 1.md 示例，URL 中带 key 参数
            url_with_key = f"{self.endpoint}?key={api_key}"

            try:
                print(f"[DEBUG] 开始发送视频分析请求，视频大小: {file_size / (1024*1024):.2f}MB")
                conn.request(
                    "POST",
                    url_with_key,
                    json.dumps(payload),
                    headers
                )

                print("[DEBUG] 等待服务器响应...")
                res = conn.getresponse()
                data = res.read()

                # 解析响应
                response_text = data.decode("utf-8")
                print(f"[DEBUG] 收到响应，状态码: {res.status}")
                response_data = json.loads(response_text)

            except TimeoutError as e:
                return {
                    "success": False,
                    "message": f"请求超时（180秒）。视频文件可能太大或网络较慢，建议使用更小的视频（<50MB）"
                }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"网络请求失败: {str(e)}"
                }
            finally:
                conn.close()
            
            # 检查响应状态
            if res.status == 200:
                # 提取分析结果
                candidates = response_data.get("candidates", [])
                if candidates:
                    content = candidates[0].get("content", {})
                    parts = content.get("parts", [])
                    
                    # 提取文本响应
                    text_response = ""
                    for part in parts:
                        if "text" in part:
                            text_response += part["text"]
                    
                    return {
                        "success": True,
                        "message": "视频分析完成",
                        "analysis": text_response,
                        "raw_response": response_data,
                        "metadata": {
                            "model": self.model,
                            "prompt": prompt,
                            "video_path": video_path,
                            "video_size": file_size,
                            "video_size_human": f"{file_size / (1024*1024):.2f}MB"
                        }
                    }
                else:
                    return {
                        "success": False,
                        "message": "未找到分析结果",
                        "raw_response": response_data
                    }
            else:
                error_msg = response_data.get("error", {}).get("message", "未知错误")
                return {
                    "success": False,
                    "message": f"API错误: {error_msg}",
                    "raw_response": response_data
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"视频分析失败: {str(e)}"
            }
    
    async def analyze_video_from_base64(
        self,
        video_base64: str,
        prompt: str = "请用3句话总结这个视频的内容",
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        分析base64编码的视频
        
        Args:
            video_base64: base64编码的视频数据
            prompt: 分析提示词
            api_key: API密钥
            
        Returns:
            分析结果
        """
        api_key = api_key or self.api_key
        
        if not api_key:
            return {
                "success": False,
                "message": "API密钥未配置"
            }
        
        try:
            # 构建请求体
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {
                                "inline_data": {
                                    "mime_type": "video/mp4",
                                    "data": video_base64
                                }
                            },
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            }

            # 发送请求（视频分析需要更长的超时时间）
            # 超时设置为180秒（3分钟）
            conn = http.client.HTTPSConnection(self.host, timeout=180)
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }

            # 根据 1.md 示例，URL 中带 key 参数
            url_with_key = f"{self.endpoint}?key={api_key}"

            try:
                print(f"[DEBUG] 开始发送base64视频分析请求")
                conn.request(
                    "POST",
                    url_with_key,
                    json.dumps(payload),
                    headers
                )

                print("[DEBUG] 等待服务器响应...")
                res = conn.getresponse()
                data = res.read()

                # 解析响应
                response_text = data.decode("utf-8")
                print(f"[DEBUG] 收到响应，状态码: {res.status}")
                response_data = json.loads(response_text)

            except TimeoutError as e:
                return {
                    "success": False,
                    "message": f"请求超时（180秒）。建议使用更小的视频文件"
                }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"网络请求失败: {str(e)}"
                }
            finally:
                conn.close()
            
            # 检查响应状态
            if res.status == 200:
                candidates = response_data.get("candidates", [])
                if candidates:
                    content = candidates[0].get("content", {})
                    parts = content.get("parts", [])
                    
                    text_response = ""
                    for part in parts:
                        if "text" in part:
                            text_response += part["text"]
                    
                    return {
                        "success": True,
                        "message": "视频分析完成",
                        "analysis": text_response,
                        "raw_response": response_data,
                        "metadata": {
                            "model": self.model,
                            "prompt": prompt
                        }
                    }
                else:
                    return {
                        "success": False,
                        "message": "未找到分析结果",
                        "raw_response": response_data
                    }
            else:
                error_msg = response_data.get("error", {}).get("message", "未知错误")
                return {
                    "success": False,
                    "message": f"API错误: {error_msg}",
                    "raw_response": response_data
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"视频分析失败: {str(e)}"
            }
    
    def get_service_name(self) -> str:
        return f"Video Analysis ({self.model})"
