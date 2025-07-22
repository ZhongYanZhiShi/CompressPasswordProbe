#!/bin/bash

echo "================================"
echo " CompressPasswordProbe 启动器"
echo "================================"
echo

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误：未找到Python3环境"
    echo "请确保已安装Python3"
    exit 1
fi

# 检查依赖
echo "正在检查依赖..."
python3 -c "import PySide6; print('✓ PySide6已安装')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "✗ PySide6未安装，正在安装..."
    pip3 install PySide6 psutil
fi

echo
echo "正在启动应用程序..."
echo
python3 main.py