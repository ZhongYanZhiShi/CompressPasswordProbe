#!/bin/bash

# CompressPasswordProbe Conda 启动脚本 (Linux/macOS)

echo "启动 CompressPasswordProbe (Conda环境)..."

# 检查 Conda 环境是否存在
if ! conda info --envs | grep -q "compress-password-probe"; then
    echo "错误: 未找到 compress-password-probe Conda 环境"
    echo "请先运行 ./install_conda.sh 进行安装"
    exit 1
fi

echo "激活 Conda 环境..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate compress-password-probe

echo "启动程序..."
python main.py
