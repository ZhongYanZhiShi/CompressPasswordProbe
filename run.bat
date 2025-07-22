@echo off
echo ================================
echo  CompressPasswordProbe 启动器
echo ================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python环境
    echo 请确保已安装Python并添加到PATH
    pause
    exit /b 1
)

REM 检查依赖
echo 正在检查依赖...
python -c "import PySide6; print('✓ PySide6已安装')" 2>nul
if errorlevel 1 (
    echo ✗ PySide6未安装，正在安装...
    pip install PySide6 psutil
)

echo.
echo 正在启动应用程序...
echo.
python main.py

if errorlevel 1 (
    echo.
    echo 程序异常退出
    pause
)