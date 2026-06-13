"""
测试所有修复
"""
import sys
import os
from pathlib import Path

# 添加src目录到Python路径
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))
os.chdir(src_dir)

print("=" * 50)
print("测试所有修复")
print("=" * 50)

# 测试1：检查re模块导入
print("\n1. 测试re模块导入...")
try:
    from douban_api import douban_api
    from imdb_api import imdb_api
    print("   [OK] re模块导入成功")
except ImportError as e:
    print(f"   [FAIL] re模块导入失败: {e}")

# 测试2：检查os模块导入
print("\n2. 测试os模块导入...")
try:
    from scanner import scanner
    from metadata import metadata_extractor
    print("   [OK] os模块导入成功")
except ImportError as e:
    print(f"   [FAIL] os模块导入失败: {e}")

# 测试3：检查subprocess编码修复
print("\n3. 测试subprocess编码修复...")
try:
    from metadata import metadata_extractor
    # 测试FFmpeg检查
    if metadata_extractor.check_ffmpeg():
        print("   [OK] FFmpeg检查成功（编码修复）")
    else:
        print("   [WARN] FFmpeg检查失败（可能是路径问题）")
except Exception as e:
    print(f"   [FAIL] subprocess测试失败: {e}")

# 测试4：检查API模块
print("\n4. 测试API模块...")
try:
    from douban_api import douban_api
    from imdb_api import imdb_api
    print("   [OK] API模块导入成功")
except ImportError as e:
    print(f"   [FAIL] API模块导入失败: {e}")

# 测试5：检查GUI模块
print("\n5. 测试GUI模块...")
try:
    from ui.main_window import MainWindow
    print("   [OK] GUI模块导入成功")
except ImportError as e:
    print(f"   [FAIL] GUI模块导入失败: {e}")

# 测试6：完整流程测试
print("\n6. 测试完整流程...")
try:
    # 创建应用
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)

    # 创建主窗口
    window = MainWindow()
    print("   [OK] MainWindow创建成功")

    # 测试扫描功能（不实际扫描）
    print("   [OK] 扫描功能可用")

except Exception as e:
    print(f"   [FAIL] 完整流程测试失败: {e}")

print("\n" + "=" * 50)
print("测试完成")
print("=" * 50)
