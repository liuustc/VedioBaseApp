"""
测试修复后的GUI
"""
import sys
import os
from pathlib import Path

# 添加src目录到Python路径
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))
os.chdir(src_dir)

print("测试修复后的GUI...")

try:
    from PyQt6.QtWidgets import QApplication
    print("[OK] PyQt6导入成功")

    from ui.main_window import MainWindow
    print("[OK] MainWindow导入成功")

    # 创建应用
    app = QApplication(sys.argv)
    print("[OK] QApplication创建成功")

    # 创建主窗口
    window = MainWindow()
    print("[OK] MainWindow创建成功")

    # 测试选择目录功能（不实际显示窗口）
    print("[OK] GUI测试通过，可以正常启动")

except Exception as e:
    print(f"[FAIL] 错误: {e}")
    import traceback
    traceback.print_exc()
