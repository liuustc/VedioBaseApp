"""
最简单的GUI测试
"""
import sys
import os
from pathlib import Path

# 添加src目录到Python路径
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))
os.chdir(src_dir)

from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel

print("创建应用...")
app = QApplication(sys.argv)

print("创建窗口...")
window = QMainWindow()
window.setWindowTitle("测试窗口")
window.setGeometry(100, 100, 400, 300)

print("创建标签...")
label = QLabel("Hello, World!", window)
label.setGeometry(100, 100, 200, 50)

print("显示窗口...")
window.show()

print("开始事件循环...")
exit_code = app.exec()

print(f"程序结束，退出代码: {exit_code}")
