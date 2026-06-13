"""
简单的GUI测试脚本
"""
import sys
import os
from pathlib import Path

# 添加src目录到Python路径
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))
os.chdir(src_dir)

print("Python路径:", sys.path)
print("当前目录:", os.getcwd())

try:
    from PyQt6.QtWidgets import QApplication
    print("PyQt6导入成功")
except ImportError as e:
    print(f"PyQt6导入失败: {e}")
    sys.exit(1)

try:
    from ui.main_window import MainWindow
    print("MainWindow导入成功")
except ImportError as e:
    print(f"MainWindow导入失败: {e}")
    sys.exit(1)

try:
    app = QApplication(sys.argv)
    print("QApplication创建成功")

    window = MainWindow()
    print("MainWindow创建成功")

    window.show()
    print("窗口显示成功")

    print("开始事件循环...")
    app.exec()
    print("事件循环结束")

except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
