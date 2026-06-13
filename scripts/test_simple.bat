@echo off
echo 测试脚本开始
echo 当前目录: %CD%
echo Python路径: venv\Scripts\python.exe

REM 检查文件是否存在
if exist "venv\Scripts\python.exe" (
    echo Python可执行文件存在
) else (
    echo Python可执行文件不存在
)

REM 尝试运行Python
echo 正在运行Python...
venv\Scripts\python.exe -c "print('Hello from Python')"

echo 测试脚本结束
pause
