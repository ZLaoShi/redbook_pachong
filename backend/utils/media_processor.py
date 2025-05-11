import os
import subprocess
import tempfile
from pathlib import Path
import yt_dlp
from typing import Optional, Tuple
import logging
import uuid

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 确保缓存目录存在
MEDIA_CACHE_DIR = os.getenv("MEDIA_CACHE_DIR", "./media_cache")
os.makedirs(MEDIA_CACHE_DIR, exist_ok=True)

def download_video(video_url: str) -> Optional[str]:
    """
    使用yt-dlp下载视频，返回下载的视频文件路径
    """
    try:
        # 创建唯一的文件名
        output_dir = Path(MEDIA_CACHE_DIR)
        unique_id = str(uuid.uuid4())
        output_template = output_dir / f"{unique_id}.%(ext)s"
        
        ydl_opts = {
            'format': 'best',  # 选择最佳质量
            'outtmpl': str(output_template),
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            if info:
                downloaded_file = None
                # 遍历info中的文件名或从条目中获取
                if 'requested_downloads' in info:
                    for entry in info['requested_downloads']:
                        if 'filepath' in entry:
                            downloaded_file = entry['filepath']
                            break
                # 如果上面没找到，尝试从info直接获取
                if not downloaded_file and 'filepath' in info:
                    downloaded_file = info['filepath']
                
                if downloaded_file and os.path.exists(downloaded_file):
                    logger.info(f"Successfully downloaded video: {downloaded_file}")
                    return downloaded_file
                    
        logger.error(f"Failed to download video from {video_url}")
        return None
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        return None

def extract_audio_from_video(video_path: str) -> Optional[str]:
    """
    使用FFmpeg从视频中提取音频，返回音频文件路径
    """
    if not os.path.exists(video_path):
        logger.error(f"Video file not found: {video_path}")
        return None
        
    try:
        # 创建音频输出路径
        audio_path = os.path.splitext(video_path)[0] + ".mp3"
        
        # 使用FFmpeg提取音频
        command = [
            "ffmpeg",
            "-i", video_path,  # 输入视频
            "-q:a", "0",       # 设置音频质量 (0最高)
            "-map", "a",       # 只提取音频
            "-y",              # 覆盖已存在的文件
            audio_path
        ]
        
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if process.returncode != 0:
            logger.error(f"FFmpeg error: {process.stderr}")
            return None
            
        if os.path.exists(audio_path):
            logger.info(f"Successfully extracted audio: {audio_path}")
            return audio_path
            
        logger.error("Audio extraction completed, but file not found")
        return None
    except Exception as e:
        logger.error(f"Error extracting audio: {e}")
        return None

def process_video_to_audio(video_url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    下载视频并提取音频，返回(视频路径, 音频路径)
    """
    video_path = download_video(video_url)
    if not video_path:
        return None, None
        
    audio_path = extract_audio_from_video(video_path)
    return video_path, audio_path

def cleanup_media_files(file_paths: list):
    """
    清理媒体文件
    """
    for path in file_paths:
        if path and os.path.exists(path):
            try:
                os.remove(path)
                logger.info(f"Deleted file: {path}")
            except Exception as e:
                logger.error(f"Error deleting file {path}: {e}")