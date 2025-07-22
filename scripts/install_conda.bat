@echo off
chcp 65001

title CompressPasswordProbe Conda Installer

echo =====================================
echo CompressPasswordProbe Conda 安装脚本
echo =====================================
echo.

echo 检查 Conda 环境...
conda --version
if errorlevel 1 (
    echo 错误: 未找到 Conda，请先安装 Anaconda 或 Miniconda
    echo 下载地址: https://www.anaconda.com/products/distribution
    pause
    exit /b 1
)

echo.
echo 创建 Conda 环境 (compress-password-probe)...
conda create -n compress-password-probe python=3.12.11 -y
if errorlevel 1 (
    echo 错误: 创建 Conda 环境失败
    pause
    exit /b 1
)

echo.
echo 激活 Conda 环境...
call conda activate compress-password-probe

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
echo Conda 环境安装完成！
echo =====================================
echo.
echo 使用说明:
echo 1. 运行 start_conda.bat 启动程序
echo 2. 环境名称: compress-password-probe
echo 3. 如需手动激活: conda activate compress-password-probe
echo.
echo 注意: 请使用 start_conda.bat 而不是 start.bat 来启动程序

pause
