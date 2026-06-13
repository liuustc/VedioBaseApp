@echo off
chcp 65001 >nul
echo 正在启动视频库管理工具...

REM 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo 错误: 未找到虚拟环境
    echo 请先创建虚拟环境: python -m venv venv
    pause
    exit /b 1
)

echo 虚拟环境检查通过

REM 激活虚拟环境
call venv\Scripts\activate.bat

echo 虚拟环境已激活

REM 运行GUI应用
echo 正在运行GUI应用...
python run_gui.py

REM 如果GUI启动失败，尝试命令行模式
if errorlevel 1 (
    echo GUI启动失败，错误代码: %errorlevel%
    echo 尝试命令行模式...
    python src\main.py
)

echo 按任意键退出...
pause
