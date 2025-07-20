@echo off
title CompressPasswordProbe

echo 启动 CompressPasswordProbe...

if not exist venv (
    echo 错误: 未找到虚拟环境，请先运行 install.bat 进行安装
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python main.py

pause
