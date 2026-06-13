@echo off
chcp 65001 >nul
echo Starting Video Base App...
echo.

REM Check virtual environment
if not exist "venv\Scripts\python.exe" (
    echo Error: Virtual environment not found
    echo Please create virtual environment first
    pause
    exit /b 1
)

REM Run GUI application
echo Running GUI application...
venv\Scripts\python.exe run_gui.py

REM If GUI fails, show error
if errorlevel 1 (
    echo.
    echo GUI failed to start
    echo Please check the error message above
)

echo.
echo Press any key to exit...
pause
