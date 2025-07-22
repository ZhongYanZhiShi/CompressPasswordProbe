#!/bin/bash

# CompressPasswordProbe Conda 安装脚本 (Linux/macOS)

echo "====================================="
echo "CompressPasswordProbe Conda 安装脚本"
echo "====================================="
echo

# 检查 Conda
if ! command -v conda &> /dev/null; then
    echo "错误: 未找到 Conda，请先安装 Anaconda 或 Miniconda"
    echo "下载地址: https://www.anaconda.com/products/distribution"
    exit 1
fi

echo "检查 Conda 环境..."
conda --version

echo
echo "创建 Conda 环境 (compress-password-probe)..."
conda create -n compress-password-probe python=3.12.11 -y
if [ $? -ne 0 ]; then
    echo "错误: 创建 Conda 环境失败"
    exit 1
fi

echo
echo "激活 Conda 环境..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate compress-password-probe

echo
echo "升级 pip..."
python -m pip install --upgrade pip

echo
echo "安装依赖包..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "警告: 部分依赖包安装失败，可能影响 GPU 加速功能"
    echo "请检查错误信息并手动安装相关包"
fi

echo
echo "====================================="
echo "Conda 环境安装完成！"
echo "====================================="
echo
echo "使用说明:"
echo "1. 运行 ./start_conda.sh 启动程序"
echo "2. 环境名称: compress-password-probe"
echo "3. 如需手动激活: conda activate compress-password-probe"
echo
echo "注意: 请使用 ./start_conda.sh 而不是 ./start.sh 来启动程序"
