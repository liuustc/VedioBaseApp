"""
诊断脚本
检查环境和依赖
"""
import sys
import os
from pathlib import Path

print("=" * 50)
print("视频库管理工具 - 环境诊断")
print("=" * 50)

# 检查Python版本
print(f"Python版本: {sys.version}")
print(f"Python可执行文件: {sys.executable}")

# 检查当前目录
print(f"当前目录: {os.getcwd()}")

# 检查src目录
src_dir = Path(__file__).parent.parent / "src"
print(f"src目录: {src_dir}")
print(f"src目录存在: {src_dir.exists()}")

# 添加src到路径
sys.path.insert(0, str(src_dir))
print(f"Python路径已更新")

# 检查依赖
print("\n检查依赖:")

# 检查PyQt6
try:
    from PyQt6.QtWidgets import QApplication
    print("  [OK] PyQt6")
except ImportError as e:
    print(f"  [FAIL] PyQt6: {e}")

# 检查其他依赖
dependencies = [
    ('database', 'from database import database'),
    ('config', 'from config import config'),
    ('scanner', 'from scanner import scanner'),
    ('metadata', 'from metadata import metadata_extractor'),
    ('douban_api', 'from douban_api import douban_api'),
    ('imdb_api', 'from imdb_api import imdb_api'),
    ('tags', 'from tags import tag_manager'),
]

for name, import_stmt in dependencies:
    try:
        exec(import_stmt)
        print(f"  [OK] {name}")
    except ImportError as e:
        print(f"  [FAIL] {name}: {e}")

# 检查UI模块
print("\n检查UI模块:")
try:
    from ui.main_window import MainWindow
    print("  [OK] ui.main_window")
except ImportError as e:
    print(f"  [FAIL] ui.main_window: {e}")

try:
    from ui.dialogs import MovieDetailsDialog, SettingsDialog
    print("  [OK] ui.dialogs")
except ImportError as e:
    print(f"  [FAIL] ui.dialogs: {e}")

# 检查配置
print("\n检查配置:")
try:
    from config import config
    ffmpeg_path = config.get_ffmpeg_path()
    print(f"  FFmpeg路径: {ffmpeg_path}")
    print(f"  FFmpeg文件存在: {Path(ffmpeg_path).exists()}")
except Exception as e:
    print(f"  [FAIL] 配置检查: {e}")

# 检查数据库
print("\n检查数据库:")
try:
    from database import database
    stats = database.get_stats()
    print(f"  电影总数: {stats['total_movies']}")
    print(f"  标签总数: {stats['total_tags']}")
except Exception as e:
    print(f"  [FAIL] 数据库检查: {e}")

print("\n" + "=" * 50)
print("诊断完成")
print("=" * 50)
