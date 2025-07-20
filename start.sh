#!/bin/bash

# CompressPasswordProbe 启动脚本 (Linux/macOS)

echo "启动 CompressPasswordProbe..."

if [ ! -d "venv" ]; then
    echo "错误: 未找到虚拟环境，请先运行 ./install.sh 进行安装"
    exit 1
fi

source venv/bin/activate
python main.py
