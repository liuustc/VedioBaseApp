"""
目录扫描模块
遍历指定目录，识别视频文件
"""
import os
import re
from pathlib import Path
from typing import List, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from loguru import logger

from config import config

# 垃圾文件关键词（网站水印、广告文件等）
JUNK_FILE_PATTERNS = [
    r'www\.\w+\.com',
    r'www\.\w+\.net',
    r'BBEDDE',
    r'BBQDDQ',
    r'66Ys\.Co',
    r'66ys\.',
    r'dytt8899',
    r'BDYS',
    r'更多电影',
    r'高清电影',
    r'免费资源',
    r'注册会员',
    r'精彩电影',
]


def is_junk_file(file_path: str) -> bool:
    """
    判断是否为垃圾文件（网站水印、广告文件等）

    Args:
        file_path: 文件路径

    Returns:
        是否为垃圾文件
    """
    filename = os.path.basename(file_path).lower()
    for pattern in JUNK_FILE_PATTERNS:
        if re.search(pattern.lower(), filename):
            return True
    return False


class DirectoryScanner:
    """目录扫描器"""

    def __init__(self):
        self.scan_extensions = config.get_scan_extensions()
        self.max_threads = config.get("max_scan_threads", 4)

    def scan_directory(self, directory: str, progress_callback: Optional[Callable] = None) -> List[str]:
        """
        扫描指定目录，返回视频文件路径列表

        Args:
            directory: 要扫描的目录路径
            progress_callback: 进度回调函数，接收当前进度和总文件数

        Returns:
            视频文件路径列表
        """
        logger.info(f"开始扫描目录: {directory}")

        if not os.path.exists(directory):
            logger.error(f"目录不存在: {directory}")
            return []

        video_files = []

        # 使用os.walk遍历目录
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                # 检查扩展名
                _, ext = os.path.splitext(file)
                if ext.lower() in self.scan_extensions:
                    video_files.append(file_path)

        logger.info(f"扫描完成，找到 {len(video_files)} 个视频文件")
        return video_files

    def scan_directory_with_progress(self, directory: str) -> List[str]:
        """
        扫描目录并显示进度条

        Args:
            directory: 要扫描的目录路径

        Returns:
            视频文件路径列表
        """
        logger.info(f"开始扫描目录: {directory}")

        if not os.path.exists(directory):
            logger.error(f"目录不存在: {directory}")
            return []

        # 先统计文件总数（为了进度条）
        total_files = 0
        for root, _, files in os.walk(directory):
            for file in files:
                _, ext = os.path.splitext(file)
                if ext.lower() in self.scan_extensions:
                    total_files += 1

        if total_files == 0:
            logger.warning("未找到视频文件")
            return []

        # 扫描文件
        video_files = []
        with tqdm(total=total_files, desc="扫描视频文件", unit="file") as pbar:
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    _, ext = os.path.splitext(file)
                    if ext.lower() in self.scan_extensions:
                        video_files.append(file_path)
                        pbar.update(1)

        logger.info(f"扫描完成，找到 {len(video_files)} 个视频文件")
        return video_files

    def scan_directory_parallel(self, directory: str) -> List[str]:
        """
        并行扫描目录（多线程）

        Args:
            directory: 要扫描的目录路径

        Returns:
            视频文件路径列表
        """
        logger.info(f"开始并行扫描目录: {directory}")

        if not os.path.exists(directory):
            logger.error(f"目录不存在: {directory}")
            return []

        # 收集所有子目录
        subdirs = []
        for root, dirs, _ in os.walk(directory):
            subdirs.append(root)
            # 限制深度，避免过多目录
            if len(subdirs) > 100:
                break

        video_files = []

        def scan_subdir(subdir):
            """扫描单个子目录"""
            files = []
            for file in os.listdir(subdir):
                file_path = os.path.join(subdir, file)
                if os.path.isfile(file_path):
                    _, ext = os.path.splitext(file)
                    if ext.lower() in self.scan_extensions:
                        files.append(file_path)
            return files

        # 并行扫描
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = {executor.submit(scan_subdir, subdir): subdir for subdir in subdirs}

            for future in as_completed(futures):
                try:
                    files = future.result()
                    video_files.extend(files)
                except Exception as e:
                    logger.error(f"扫描子目录失败: {e}")

        logger.info(f"并行扫描完成，找到 {len(video_files)} 个视频文件")
        return video_files

    def get_file_info(self, file_path: str) -> dict:
        """
        获取文件基本信息

        Args:
            file_path: 文件路径

        Returns:
            文件信息字典
        """
        try:
            stat = os.stat(file_path)
            return {
                'file_path': file_path,
                'file_size': stat.st_size,
                'modified_time': stat.st_mtime,
                'created_time': stat.st_ctime
            }
        except Exception as e:
            logger.error(f"获取文件信息失败 {file_path}: {e}")
            return {
                'file_path': file_path,
                'file_size': 0,
                'modified_time': 0,
                'created_time': 0
            }


# 全局扫描器实例
scanner = DirectoryScanner()
