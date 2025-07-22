# Scripts 文件夹说明

这个文件夹包含了 CompressPasswordProbe 项目的详细安装和启动脚本。

## 文件说明

### 安装脚本

| 文件名 | 平台 | 功能 |
|--------|------|------|
| `install.bat` | Windows | 使用虚拟环境安装依赖 |
| `install.sh` | Linux/macOS | 使用虚拟环境安装依赖 |
| `install_conda.bat` | Windows | 使用Conda环境安装依赖 |
| `install_conda.sh` | Linux/macOS | 使用Conda环境安装依赖 |

### 启动脚本

| 文件名 | 平台 | 功能 |
|--------|------|------|
| `start_conda.bat` | Windows | 使用Conda环境启动程序 |
| `start_conda.sh` | Linux/macOS | 使用Conda环境启动程序 |

## 推荐使用方式

**直接运行根目录的 `start.bat`/`start.sh`** - 这是最简单的方式！

这些脚本会：


1. 🔍 自动检测已配置的环境
2. 🚀 直接启动程序（如果环境已配置）
3. 📦 提供安装选项（如果环境未配置）
4. ⚡ 安装完成后自动启动程序

## 高级用户

如果您需要特定的安装方式，可以直接运行此文件夹中的对应脚本：

- **虚拟环境**: `./scripts/install.bat` 或 `./scripts/install.sh`
- **Conda环境**: `./scripts/install_conda.bat` 或 `./scripts/install_conda.sh`
