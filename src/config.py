"""
配置管理模块
管理FFmpeg路径、API密钥等配置信息
"""
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any


class Config:
    """配置管理类"""

    def __init__(self):
        # 配置文件路径：用户目录下的配置文件
        self.config_dir = Path.home() / ".VideoBaseApp"
        self.config_file = self.config_dir / "config.json"

        # 默认配置
        self.default_config = {
            "ffmpeg_path": r"E:\ffmpeg-2023-05-08-git-2d43c23b81-full_build\bin\ffmpeg.exe",
            "douban_enabled": True,
            "imdb_enabled": True,
            "imdb_api_key": "286bddae",
            "scan_extensions": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".rmvb", ".rm"],
            "max_scan_threads": 4,
            "cache_dir": str(Path.home() / ".VideoBaseApp" / "cache"),
            "last_directory": ""  # 上次打开的目录
        }

        self.config = self.default_config.copy()
        self.load_config()

    def load_config(self):
        """加载配置文件"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 合并配置，保留默认值中不存在的键
                    for key, value in loaded_config.items():
                        if key in self.default_config:
                            self.config[key] = value
                print(f"配置已加载: {self.config_file}")
            else:
                print(f"配置文件不存在，使用默认配置")
                self.save_config()
        except Exception as e:
            print(f"加载配置失败: {e}")
            self.config = self.default_config.copy()

    def save_config(self):
        """保存配置文件"""
        try:
            # 确保配置目录存在
            self.config_dir.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"配置已保存: {self.config_file}")
        except Exception as e:
            print(f"保存配置失败: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """设置配置项"""
        if key in self.default_config:
            self.config[key] = value
        else:
            # 允许添加新配置项
            self.config[key] = value

    def get_ffmpeg_path(self) -> str:
        """获取FFmpeg路径"""
        return self.get("ffmpeg_path", self.default_config["ffmpeg_path"])

    def set_ffmpeg_path(self, path: str):
        """设置FFmpeg路径"""
        self.set("ffmpeg_path", path)
        self.save_config()

    def get_imdb_api_key(self) -> str:
        """获取IMDb API密钥"""
        return self.get("imdb_api_key", self.default_config["imdb_api_key"])

    def set_imdb_api_key(self, key: str):
        """设置IMDb API密钥"""
        self.set("imdb_api_key", key)
        self.save_config()

    def get_scan_extensions(self) -> list:
        """获取扫描扩展名列表"""
        return self.get("scan_extensions", self.default_config["scan_extensions"])

    def get_cache_dir(self) -> Path:
        """获取缓存目录"""
        cache_dir = Path(self.get("cache_dir", self.default_config["cache_dir"]))
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

    def get_last_directory(self) -> str:
        """获取上次打开的目录"""
        return self.get("last_directory", "")

    def set_last_directory(self, directory: str):
        """设置上次打开的目录"""
        self.set("last_directory", directory)
        self.save_config()


# 全局配置实例
config = Config()
