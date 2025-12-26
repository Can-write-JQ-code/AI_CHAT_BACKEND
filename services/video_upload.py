import os
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import UploadFile, HTTPException
from pathlib import Path
import aiofiles
from datetime import datetime

class VideoUploadService:
    """视频上传服务，处理视频文件的上传、存储和管理"""
    
    def __init__(self, upload_dir: str = "uploads/videos"):
        """
        初始化视频上传服务
        
        Args:
            upload_dir: 视频存储目录路径
        """
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # 允许的视频格式
        self.allowed_formats = {
            'video/mp4',
            'video/avi', 
            'video/mov',
            'video/wmv',
            'video/flv',
            'video/mkv',
            'video/webm'
        }
        
        # 最大文件大小 (500MB)
        self.max_file_size = 500 * 1024 * 1024
    
    async def upload_video(self, file: UploadFile) -> Dict[str, Any]:
        """
        上传视频文件
        
        Args:
            file: 上传的视频文件
            
        Returns:
            包含上传结果的字典
        """
        try:
            # 验证文件类型
            if file.content_type not in self.allowed_formats:
                raise HTTPException(
                    status_code=400,
                    detail=f"不支持的视频格式: {file.content_type}. 支持的格式: {', '.join([fmt.split('/')[1] for fmt in self.allowed_formats])}"
                )
            
            # 读取文件内容以验证大小
            contents = await file.read()
            file_size = len(contents)
            
            if file_size > self.max_file_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"文件大小超过限制: {file_size / (1024*1024):.1f}MB / {self.max_file_size / (1024*1024):.0f}MB"
                )
            
            # 生成唯一文件名
            file_ext = Path(file.filename).suffix or '.mp4'
            unique_filename = f"video_{uuid.uuid4().hex}{file_ext}"
            file_path = self.upload_dir / unique_filename
            
            # 保存文件
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(contents)
            
            # 获取文件信息
            file_info = {
                "success": True,
                "message": "视频上传成功",
                "filename": file.filename,
                "stored_filename": unique_filename,
                "file_path": str(file_path),
                "size": file_size,
                "size_human": f"{file_size / (1024*1024):.2f}MB",
                "format": file.content_type,
                "upload_time": datetime.now().isoformat(),
                "url": f"/api/videos/{unique_filename}"
            }
            
            return file_info
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"视频上传失败: {str(e)}"
            )
    
    async def get_video_info(self, filename: str) -> Dict[str, Any]:
        """
        获取视频文件信息
        
        Args:
            filename: 存储的文件名
            
        Returns:
            视频信息字典
        """
        file_path = self.upload_dir / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"视频文件不存在: {filename}"
            )
        
        stat = file_path.stat()
        
        return {
            "filename": filename,
            "file_path": str(file_path),
            "size": stat.st_size,
            "size_human": f"{stat.st_size / (1024*1024):.2f}MB",
            "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "url": f"/api/videos/{filename}"
        }
    
    async def delete_video(self, filename: str) -> Dict[str, Any]:
        """
        删除视频文件
        
        Args:
            filename: 存储的文件名
            
        Returns:
            删除结果字典
        """
        file_path = self.upload_dir / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"视频文件不存在: {filename}"
            )
        
        try:
            file_path.unlink()
            return {
                "success": True,
                "message": f"视频 {filename} 已删除",
                "filename": filename
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"删除视频失败: {str(e)}"
            )
    
    def list_videos(self) -> Dict[str, Any]:
        """
        列出所有上传的视频
        
        Returns:
            视频列表
        """
        videos = []
        
        for file_path in self.upload_dir.glob("*"):
            if file_path.is_file():
                stat = file_path.stat()
                videos.append({
                    "filename": file_path.name,
                    "size": stat.st_size,
                    "size_human": f"{stat.st_size / (1024*1024):.2f}MB",
                    "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "url": f"/api/videos/{file_path.name}"
                })
        
        return {
            "count": len(videos),
            "videos": sorted(videos, key=lambda x: x['created_time'], reverse=True)
        }
    
    def get_service_name(self) -> str:
        return "Video Upload Service"
