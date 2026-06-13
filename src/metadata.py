"""
元数据提取模块
从视频文件中提取时长等信息
"""
import os
import re
import subprocess
from pathlib import Path
from typing import Optional
from loguru import logger
from config import config


class MetadataExtractor:
    """元数据提取器"""

    def __init__(self):
        self.ffmpeg_path = config.get_ffmpeg_path()

    def check_ffmpeg(self) -> bool:
        """检查ffmpeg是否可用"""
        try:
            import moviepy
            return True
        except ImportError:
            logger.error("moviepy未安装")
            return False

    def _extract_duration_from_ffmpeg_output(self, video_path: str) -> Optional[int]:
        """
        直接用ffmpeg获取时长，从输出中解析
        这是备用方案，当moviepy失败时使用
        """
        try:
            cmd = [self.ffmpeg_path, '-i', video_path]
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            # ffmpeg -i 输出到stderr
            output = result.stderr

            # 用正则匹配时长: Duration: HH:MM:SS.xx
            duration_pattern = r'Duration:\s*(\d{2}):(\d{2}):(\d{2})\.(\d{2})'
            match = re.search(duration_pattern, output)

            if match:
                hours = int(match.group(1))
                minutes = int(match.group(2))
                seconds = int(match.group(3))
                total_seconds = hours * 3600 + minutes * 60 + seconds
                logger.info(f"用ffmpeg正则提取时长成功: {video_path} -> {total_seconds}秒")
                return total_seconds

            # 备用：尝试匹配秒数格式
            duration_seconds_pattern = r'Duration:\s*([\d.]+)\s*seconds'
            match = re.search(duration_seconds_pattern, output)
            if match:
                total_seconds = int(float(match.group(1)))
                logger.info(f"用ffmpeg正则提取时长成功: {video_path} -> {total_seconds}秒")
                return total_seconds

            logger.warning(f"无法从ffmpeg输出解析时长: {video_path}")
            return None

        except Exception as e:
            logger.error(f"用ffmpeg提取时长异常: {e}")
            return None

    def get_video_duration(self, video_path: str) -> Optional[int]:
        """
        获取视频时长（秒）

        Args:
            video_path: 视频文件路径

        Returns:
            时长（秒），失败返回None
        """
        if not os.path.exists(video_path):
            logger.error(f"视频文件不存在: {video_path}")
            return None

        # 方法1：使用moviepy
        try:
            from moviepy import VideoFileClip
            logger.info(f"正在用moviepy获取时长: {video_path}")
            clip = VideoFileClip(video_path)
            duration = clip.duration
            clip.close()

            if duration:
                logger.info(f"moviepy获取时长成功: {video_path} -> {duration}秒")
                return int(duration)
            else:
                logger.warning(f"moviepy获取时长失败，尝试ffmpeg方案")

        except ImportError as e:
            logger.error(f"moviepy导入失败: {e}")
        except Exception as e:
            logger.warning(f"moviepy获取时长异常，尝试ffmpeg方案: {e}")

        # 方法2：直接用ffmpeg（备用方案）
        logger.info(f"使用ffmpeg备用方案获取时长: {video_path}")
        return self._extract_duration_from_ffmpeg_output(video_path)


# 全局实例
metadata_extractor = MetadataExtractor()
