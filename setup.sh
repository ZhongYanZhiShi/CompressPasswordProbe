#!/bin/bash

# CompressPasswordProbe 压缩密码破解工具

echo "=========================================="
echo "  CompressPasswordProbe 压缩密码破解工具"
echo "=========================================="
echo

echo "正在检测环境..."

# 检查虚拟环境
if [ -d "venv" ]; then
    echo "✓ 检测到虚拟环境 (venv)"
    echo "启动程序..."
    source venv/bin/activate
    python main.py
    exit 0
fi

# 检查Conda环境
if conda info --envs | grep -q "compress-password-probe"; then
    echo "✓ 检测到 Conda 环境 (compress-password-probe)"
    echo "启动程序..."
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate compress-password-probe
    python main.py
    exit 0
fi

# 没有找到配置好的环境
echo
echo "⚠ 未检测到已配置的Python环境"
echo
echo "请选择安装方式："
echo
echo "[1] 虚拟环境 (venv)     - 轻量级，传统方式"
echo "[2] Conda 环境         - 推荐，更好的包管理"
echo "[3] 手动安装           - 高级用户"
echo "[4] 查看帮助文档"
echo "[0] 退出"
echo

read -p "请输入选择 (0-4): " choice

case $choice in
    1)
        echo
        echo "开始虚拟环境安装..."
        chmod +x scripts/install.sh
        ./scripts/install.sh
        if [ $? -eq 0 ]; then
            echo
            echo "安装完成，正在启动程序..."
            source venv/bin/activate
            python main.py
        fi
        ;;
    2)
        echo
        echo "开始Conda环境安装..."
        chmod +x scripts/install_conda.sh
        ./scripts/install_conda.sh
        if [ $? -eq 0 ]; then
            echo
            echo "安装完成，正在启动程序..."
            source $(conda info --base)/etc/profile.d/conda.sh
            conda activate compress-password-probe
            python main.py
        fi
        ;;
    3)
        echo
        echo "手动安装说明:"
        echo "1. 确保已安装 Python 3.8+ 或 Anaconda"
        echo "2. 运行: pip install -r requirements.txt"
        echo "3. 运行: python main.py"
        echo
        ;;
    4)
        echo
        echo "正在打开帮助文档..."
        if [ -f "README.md" ]; then
            if command -v xdg-open > /dev/null; then
                xdg-open README.md
            elif command -v open > /dev/null; then
                open README.md
            else
                cat README.md
            fi
        else
            echo "未找到帮助文档"
        fi
        ;;
    0)
        echo "退出安装向导"
        exit 0
        ;;
    *)
        echo "无效选择，请重新运行脚本"
        exit 1
        ;;
esac

echo
echo "=========================================="
echo "感谢使用 CompressPasswordProbe！"
echo "=========================================="
