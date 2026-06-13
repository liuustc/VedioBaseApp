@echo off
echo ========================================
echo 视频库管理工具 - 环境诊断
echo ========================================
echo.

echo 1. 检查Python...
where python
python --version
echo.

echo 2. 检查虚拟环境...
if exist "venv\Scripts\python.exe" (
    echo [OK] 虚拟环境存在
    venv\Scripts\python --version
) else (
    echo [FAIL] 虚拟环境不存在
    echo 请运行: python -m venv venv
)
echo.

echo 3. 检查依赖...
venv\Scripts\pip list | findstr /i "PyQt6 moviepy requests pillow opencv-python tqdm loguru"
echo.

echo 4. 检查配置文件...
if exist "%USERPROFILE%\.VideoBaseApp\config.json" (
    echo [OK] 配置文件存在
    type "%USERPROFILE%\.VideoBaseApp\config.json"
) else (
    echo [FAIL] 配置文件不存在
)
echo.

echo 5. 检查FFmpeg...
if exist "E:\ffmpeg-2023-05-08-git-2d43c23b81-full_build\bin\ffmpeg.exe" (
    echo [OK] FFmpeg存在
) else (
    echo [FAIL] FFmpeg不存在
    echo 请检查配置文件中的ffmpeg_path
)
echo.

echo 6. 测试Python导入...
venv\Scripts\python -c "import sys; sys.path.insert(0, 'src'); from PyQt6.QtWidgets import QApplication; print('[OK] PyQt6导入成功')"
echo.

echo ========================================
echo 诊断完成
echo ========================================
pause
