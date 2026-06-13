@echo off
echo 正在启动视频库管理工具...

REM 检查虚拟环境
if not exist "venv\Scripts\python.exe" (
    echo 错误: 未找到虚拟环境
    pause
    exit /b 1
)

REM 运行GUI
echo 运行GUI应用...
venv\Scripts\python.exe run_gui_debug.py

REM 如果失败，显示错误
if errorlevel 1 (
    echo GUI启动失败，错误代码: %errorlevel%
    pause
    exit /b 1
)

echo GUI已关闭
pause
