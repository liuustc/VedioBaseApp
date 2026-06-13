@echo off
chcp 65001 >nul
echo Starting Video Base App...

REM Check virtual environment
if not exist "venv\Scripts\python.exe" (
    echo Error: Virtual environment not found
    pause
    exit /b 1
)

REM Run GUI application
venv\Scripts\python.exe run_gui.py

REM Exit when GUI closes
exit
