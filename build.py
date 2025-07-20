"""
构建脚本 - 用于打包可执行文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, description):
    """运行命令并显示进度"""
    print(f"\n{'='*50}")
    print(f"{description}")
    print(f"{'='*50}")

    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"错误: {e}")
        print(f"输出: {e.stdout}")
        print(f"错误信息: {e.stderr}")
        return False


def clean_build():
    """清理构建目录"""
    directories_to_clean = ["build", "dist", "__pycache__"]

    for directory in directories_to_clean:
        if os.path.exists(directory):
            print(f"清理目录: {directory}")
            shutil.rmtree(directory)


def install_pyinstaller():
    """安装 PyInstaller"""
    return run_command("pip install pyinstaller", "安装 PyInstaller")


def build_executable():
    """构建可执行文件"""
    spec_file = "CompressPasswordProbe.spec"

    if not os.path.exists(spec_file):
        print(f"错误: 未找到规格文件 {spec_file}")
        return False

    return run_command(f"pyinstaller {spec_file}", "构建可执行文件")


def create_package():
    """创建发布包"""
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("错误: 未找到 dist 目录")
        return False

    # 复制必要文件到 dist 目录
    files_to_copy = ["README.md", "LICENSE", "sample_dictionary.txt"]

    for file_name in files_to_copy:
        if os.path.exists(file_name):
            shutil.copy2(file_name, dist_dir)
            print(f"复制文件: {file_name}")

    print("发布包创建完成!")
    return True


def main():
    """主函数"""
    print("CompressPasswordProbe 构建脚本")
    print("=" * 50)

    # 检查 Python 版本
    if sys.version_info < (3, 8):
        print("错误: 需要 Python 3.8 或更高版本")
        return False

    # 清理旧的构建文件
    clean_build()

    # 安装 PyInstaller
    if not install_pyinstaller():
        print("安装 PyInstaller 失败")
        return False

    # 构建可执行文件
    if not build_executable():
        print("构建可执行文件失败")
        return False

    # 创建发布包
    if not create_package():
        print("创建发布包失败")
        return False

    print("\n" + "=" * 50)
    print("构建完成!")
    print("可执行文件位于 dist/ 目录中")
    print("=" * 50)

    return True


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
