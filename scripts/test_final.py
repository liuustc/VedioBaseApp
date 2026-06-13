"""
最终测试脚本
验证所有修复和新增功能
"""
import sys
import os
from pathlib import Path

# 添加src目录到Python路径
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))
os.chdir(src_dir)

print("=" * 60)
print("最终测试 - 验证所有修复和新增功能")
print("=" * 60)

# 测试1：检查所有模块导入
print("\n1. 测试模块导入...")
modules = [
    ('config', 'from config import config'),
    ('database', 'from database import database'),
    ('scanner', 'from scanner import scanner'),
    ('metadata', 'from metadata import metadata_extractor'),
    ('douban_api', 'from douban_api import douban_api'),
    ('imdb_api', 'from imdb_api import imdb_api'),
    ('tags', 'from tags import tag_manager'),
]

for name, import_stmt in modules:
    try:
        exec(import_stmt)
        print(f"   [OK] {name}")
    except ImportError as e:
        print(f"   [FAIL] {name}: {e}")

# 测试2：检查UI模块
print("\n2. 测试UI模块...")
try:
    from ui.main_window import MainWindow
    from ui.dialogs import MovieDetailsDialog, SettingsDialog
    print("   [OK] UI模块导入成功")
except ImportError as e:
    print(f"   [FAIL] UI模块导入失败: {e}")

# 测试3：检查配置功能
print("\n3. 测试配置功能...")
try:
    from config import config

    # 测试上次目录功能
    last_dir = config.get_last_directory()
    print(f"   [OK] 上次目录功能正常 (当前: '{last_dir}')")

    # 测试设置上次目录
    test_dir = "H:\\test_directory"
    config.set_last_directory(test_dir)
    if config.get_last_directory() == test_dir:
        print(f"   [OK] 设置上次目录功能正常")
    else:
        print(f"   [FAIL] 设置上次目录功能异常")
except Exception as e:
    print(f"   [FAIL] 配置功能测试失败: {e}")

# 测试4：检查Qt API修复
print("\n4. 测试Qt API修复...")
try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QTableWidgetItem

    # 测试Qt.AlignmentFlag
    item = QTableWidgetItem()
    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    print("   [OK] Qt.AlignmentFlag.AlignCenter 正常")

    # 测试Qt.CheckState
    item.setCheckState(Qt.CheckState.Unchecked)
    print("   [OK] Qt.CheckState.Unchecked 正常")

    # 测试Qt.ItemDataRole
    item.setData(Qt.ItemDataRole.UserRole, 123)
    print("   [OK] Qt.ItemDataRole.UserRole 正常")

except Exception as e:
    print(f"   [FAIL] Qt API测试失败: {e}")

# 测试5：检查subprocess编码修复
print("\n5. 测试subprocess编码修复...")
try:
    from metadata import metadata_extractor
    # 测试FFmpeg检查（编码修复）
    if metadata_extractor.check_ffmpeg():
        print("   [OK] FFmpeg检查成功（编码修复）")
    else:
        print("   [WARN] FFmpeg检查失败（可能是路径问题）")
except Exception as e:
    print(f"   [FAIL] subprocess测试失败: {e}")

# 测试6：完整GUI测试
print("\n6. 测试完整GUI...")
try:
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)

    # 创建主窗口
    window = MainWindow()
    print("   [OK] MainWindow创建成功")

    # 检查上次目录是否加载
    if window.current_directory:
        print(f"   [OK] 上次目录已加载: {window.current_directory}")
    else:
        print("   [OK] 无上次目录（首次使用）")

except Exception as e:
    print(f"   [FAIL] GUI测试失败: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
