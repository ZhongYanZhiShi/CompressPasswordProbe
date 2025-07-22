@echo off
title CompressPasswordProbe (Conda)

echo 启动 CompressPasswordProbe (Conda环境)...

echo 检查 Conda 环境...
conda info --envs | findstr "compress-password-probe" >nul
if errorlevel 1 (
    echo 错误: 未找到 compress-password-probe Conda 环境
    echo 请先运行 install_conda.bat 进行安装
    pause
    exit /b 1
)

echo 激活 Conda 环境...
call conda activate compress-password-probe

echo 启动程序...
python main.py

echo.
echo 程序已退出，按任意键关闭窗口...
pause
