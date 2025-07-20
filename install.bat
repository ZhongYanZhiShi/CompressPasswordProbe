@echo off
title CompressPasswordProbe Installer

echo =====================================
echo CompressPasswordProbe 安装脚本
echo =====================================
echo.

echo 检查 Python 环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python 3.8 或更高版本
    pause
    exit /b 1
)

echo.
echo 创建虚拟环境...
python -m venv venv
if errorlevel 1 (
    echo 错误: 创建虚拟环境失败
    pause
    exit /b 1
)

echo.
echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo.
echo 升级 pip...
python -m pip install --upgrade pip

echo.
echo 安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo 警告: 部分依赖包安装失败，可能影响 GPU 加速功能
    echo 请检查错误信息并手动安装相关包
)

echo.
echo =====================================
echo 安装完成！
echo =====================================
echo.
echo 使用说明:
echo 1. 运行 start.bat 启动程序
echo 2. 或者在虚拟环境中运行: python main.py
echo.
pause
