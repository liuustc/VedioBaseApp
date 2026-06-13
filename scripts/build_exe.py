"""
打包脚本
使用PyInstaller将应用打包成exe文件
"""
import os
import sys
import subprocess
from pathlib import Path


def check_pyinstaller():
    """检查PyInstaller是否安装"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False


def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("PyInstaller安装成功")
        return True
    except subprocess.CalledProcessError:
        print("安装PyInstaller失败")
        return False


def build_exe():
    """打包exe"""
    # 检查PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            print("无法继续打包")
            return

    # 获取项目根目录
    project_dir = Path(__file__).parent
    src_dir = project_dir / "src"
    run_gui = project_dir / "run_gui.py"

    # PyInstaller命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=VideoBaseApp",
        "--onefile",  # 单文件
        "--windowed",  # 无控制台窗口
        "--clean",  # 清理临时文件
        "--noconfirm",  # 不确认覆盖
        f"--icon={project_dir / 'icon.ico'}",  # 图标（如果存在）
        f"--add-data={src_dir};src",  # 添加src目录
        f"--add-data={project_dir / 'data'};data",  # 添加data目录
        "--hidden-import=PyQt6.sip",  # 隐藏导入
        "--hidden-import=moviepy",  # 隐藏导入
        str(run_gui)
    ]

    # 移除不存在的图标参数
    icon_path = project_dir / "icon.ico"
    if not icon_path.exists():
        cmd = [arg for arg in cmd if not arg.startswith("--icon=")]

    print("开始打包...")
    print("命令:", " ".join(cmd))

    try:
        result = subprocess.run(cmd, cwd=project_dir, check=True)
        print("\n打包成功！")
        print(f"exe文件位于: {project_dir / 'dist' / 'VideoBaseApp.exe'}")
    except subprocess.CalledProcessError as e:
        print(f"\n打包失败: {e}")
        print("请检查错误信息并重试")


def main():
    """主函数"""
    print("=== 视频库管理工具打包脚本 ===\n")

    # 检查是否在虚拟环境中
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("当前在虚拟环境中，建议在虚拟环境中打包")
    else:
        print("警告: 当前不在虚拟环境中，建议使用虚拟环境打包")

    build_exe()

    print("\n=== 打包完成 ===")


if __name__ == '__main__':
    main()
