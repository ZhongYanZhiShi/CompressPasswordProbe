@echo off
chcp 65001
title CompressPasswordProbe

echo ==========================================
echo   CompressPasswordProbe 压缩密码破解工具
echo ==========================================
echo.

REM 首先尝试智能启动
echo 正在检测环境...

REM 检查是否存在虚拟环境
if exist venv (
    echo ✓ 检测到虚拟环境 ^(venv^)
    echo 启动程序...
    call venv\Scripts\activate.bat
    python main.py
    goto :end
)

REM 检查是否存在 Conda 环境
conda info --envs | findstr "compress-password-probe" >nul 2>&1
if not errorlevel 1 (
    echo ✓ 检测到 Conda 环境 ^(compress-password-probe^)
    echo 启动程序...
    call conda activate compress-password-probe
    python main.py
    goto :end
)

REM 没有找到配置好的环境，显示安装选项
echo.
echo ⚠ 未检测到已配置的Python环境
echo.
echo 请选择安装方式：
echo.
echo [1] 虚拟环境 (venv)     - 轻量级，传统方式
echo [2] Conda 环境         - 推荐，更好的包管理
echo [3] 手动安装           - 高级用户
echo [4] 查看帮助文档
echo [0] 退出
echo.

set /p choice="请输入选择 (0-4): "

if "%choice%"=="1" (
    echo.
    echo 开始虚拟环境安装...
    call scripts\install.bat
    if not errorlevel 1 (
        echo.
        echo 安装完成，正在启动程序...
        call venv\Scripts\activate.bat
        python main.py
    )
    goto :end
)

if "%choice%"=="2" (
    echo.
    echo 开始Conda环境安装...
    call scripts\install_conda.bat
    if not errorlevel 1 (
        echo.
        echo 安装完成，正在启动程序...
        call conda activate compress-password-probe
        python main.py
    )
    goto :end
)

if "%choice%"=="3" (
    echo.
    echo 手动安装说明:
    echo 1. 确保已安装 Python 3.8+ 或 Anaconda
    echo 2. 运行: pip install -r requirements.txt
    echo 3. 运行: python main.py
    echo.
    goto :end
)

if "%choice%"=="4" (
    echo.
    echo 正在打开帮助文档...
    if exist README.md (
        start README.md
    ) else (
        echo 未找到帮助文档
    )
    goto :end
)

if "%choice%"=="0" (
    echo 退出安装向导
    goto :end
)

echo 无效选择，请重新运行脚本
pause
exit /b 1

:end
echo.
echo ==========================================
echo 感谢使用 CompressPasswordProbe！
echo ==========================================
pause
