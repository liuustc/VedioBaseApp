@echo off
chcp 65001 >nul
echo Starting Video Base App...

REM Check virtual environment
if not exist "venv\Scripts\python.exe" (
    echo Error: Virtual environment not found
    pause
    exit /b 1
)

echo Virtual environment found

REM Run GUI application
echo Running GUI application...
venv\Scripts\python.exe run_gui.py

REM If GUI fails, try command line mode
if errorlevel 1 (
    echo GUI failed, trying command line mode...
    venv\Scripts\python.exe src\main.py
)

echo Press any key to exit...
pause
