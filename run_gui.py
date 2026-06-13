"""
启动脚本
运行视频库管理工具的GUI界面
"""
import sys
from pathlib import Path

# 添加src目录到Python路径
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# 导入并运行GUI
from ui.main_window import run_gui

if __name__ == '__main__':
    run_gui()
