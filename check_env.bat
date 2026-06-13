@echo off
chcp 65001 >nul
echo ========================================
echo Video Base App - Environment Check
echo ========================================
echo.

echo 1. Checking Python...
where python
python --version
echo.

echo 2. Checking virtual environment...
if exist "venv\Scripts\python.exe" (
    echo [OK] Virtual environment exists
    venv\Scripts\python --version
) else (
    echo [FAIL] Virtual environment not found
    echo Run: python -m venv venv
)
echo.

echo 3. Checking dependencies...
venv\Scripts\pip list | findstr /i "PyQt6 moviepy requests pillow opencv-python tqdm loguru"
echo.

echo 4. Testing Python import...
venv\Scripts\python -c "import sys; sys.path.insert(0, 'src'); from PyQt6.QtWidgets import QApplication; print('[OK] PyQt6 imported successfully')"
echo.

echo ========================================
echo Check complete
echo ========================================
pause
