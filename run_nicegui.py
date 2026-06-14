"""
NiceGUI 启动脚本
"""
import sys
from pathlib import Path

# 添加src目录到Python路径
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from ui_nicegui.app import run_nicegui

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='VideoBaseApp NiceGUI Web 界面')
    parser.add_argument('--port', type=int, default=8080, help='服务端口 (默认: 8080)')
    args = parser.parse_args()
    run_nicegui(port=args.port)
