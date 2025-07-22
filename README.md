# CompressPasswordProbe

基于 Python 3 和 PySide6 的图形界面压缩文件密码破解工具，支持通过字典遍历测试解密压缩文件的密码。

## 功能特性

### 核心功能

- **多格式支持**: 支持 ZIP、7Z、RAR 格式的压缩文件
- **字典攻击**: 支持加载自定义字典文件进行密码破解
- **拖放操作**: 支持拖拽文件到窗口进行快速加载
- **GPU 加速**: 可选的 GPU 加速功能，支持 CUDA 和 OpenCL
- **实时进度**: 显示破解进度、当前尝试密码和测试速度
- **多线程处理**: 异步处理，确保界面响应流畅

### 用户界面

- **直观操作**: 清晰的界面布局，易于理解和操作
- **进度反馈**: 实时显示测试进度条和详细信息
- **日志记录**: 完整的操作日志和结果记录
- **设置管理**: 丰富的配置选项，支持个性化设置

## 系统要求

### 最低要求

- Python 3.8 或更高版本
- Windows 10 / macOS 10.14 / Ubuntu 18.04 或更高版本
- 至少 4GB RAM
- 100MB 可用磁盘空间

### GPU 加速要求（可选）

- NVIDIA GPU（支持 CUDA）或 AMD GPU（支持 OpenCL）
- 相应的 GPU 驱动程序
- CUDA Toolkit 或 OpenCL SDK

## 安装说明

## 快速开始

### 🚀 一键启动（推荐）

```bash
# 克隆仓库
git clone https://github.com/ZhongYanZhiShi/CompressPasswordProbe.git
cd CompressPasswordProbe

# Windows 用户
start.bat

# Linux/macOS 用户
chmod +x start.sh
./start.sh
```

**就这么简单！** `start` 脚本会自动：
- 🔍 检测已配置的环境
- 🚀 直接启动程序（如果环境已配置）
- 📦 提供安装向导（如果环境未配置）
- ⚡ 安装完成后自动启动程序

## 安装说明

### 方式一：从源码安装（推荐）

1. **克隆仓库**

```bash
git clone https://github.com/ZhongYanZhiShi/CompressPasswordProbe.git
cd CompressPasswordProbe
```

2. **运行启动脚本**

```bash
# Windows
start.bat

# Linux/macOS  
./start.sh
```

### 方式二：使用可执行文件

1. 从 [Releases](https://github.com/ZhongYanZhiShi/CompressPasswordProbe/releases) 页面下载对应平台的可执行文件
2. 解压下载的文件
3. 直接运行 `CompressPasswordProbe.exe`（Windows）或相应的可执行文件

### 方式三：使用 Conda 环境（推荐）

Conda 环境提供更好的包管理和依赖解析能力，特别适合科学计算和机器学习相关的应用。

#### Windows 用户

```batch
# 安装 Conda 环境并依赖
scripts\install_conda.bat

# 启动程序
scripts\start_conda.bat
```

#### Linux/macOS 用户

```bash
# 安装 Conda 环境并依赖
./scripts/install_conda.sh

# 启动程序
./scripts/start_conda.sh
```

#### 手动安装 Conda 环境

如果您更喜欢手动控制安装过程：

```bash
# 创建 Conda 环境
conda create -n compress-password-probe python=3.11 -y

# 激活环境
conda activate compress-password-probe

# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

**注意**: 详细的 Conda 使用指南请参考 [CONDA_GUIDE.md](CONDA_GUIDE.md)

## 使用指南

### 基本使用流程

1. **加载压缩文件**
   - 点击"浏览..."按钮选择压缩文件
   - 或直接拖拽压缩文件到窗口的拖放区域

2. **选择字典文件**
   - 点击"浏览..."按钮选择字典文件（.txt格式）
   - 或使用"创建示例字典"功能生成测试字典

3. **配置选项**
   - 根据需要启用或禁用 GPU 加速
   - 在设置中调整线程数、批处理大小等参数

4. **开始破解**
   - 点击"开始破解"按钮启动密码测试
   - 观察实时进度和速度信息

5. **查看结果**
   - 破解成功时会显示找到的密码
   - 查看详细的日志信息

### 字典文件格式

字典文件应为纯文本格式（.txt），每行一个密码：

```
123456
password
admin
qwerty
12345678
```

### GPU 加速设置

1. **检查 GPU 支持**
   - 打开"设置" → "GPU"选项卡
   - 查看 GPU 检测结果

2. **安装 GPU 依赖**
   - **NVIDIA GPU**: 安装 CUDA Toolkit 和 `pycuda`
   - **AMD GPU**: 安装 OpenCL SDK 和 `pyopencl`

3. **启用 GPU 加速**
   - 在主界面勾选"启用GPU加速"
   - 或在设置中配置相关选项

## 依赖库

### 核心依赖

- **PySide6**: GUI 框架
- **py7zr**: 7Z 格式支持
- **rarfile**: RAR 格式支持
- **zipfile**: ZIP 格式支持（Python 标准库）

### GPU 加速依赖（可选）

- **pycuda**: CUDA 支持
- **pyopencl**: OpenCL 支持
- **numba**: JIT 编译器

### 其他依赖

- **psutil**: 系统信息获取

## 项目结构

```
CompressPasswordProbe/
├── main.py                 # 主入口文件
├── start.bat              # Windows 智能启动脚本
├── start.sh               # Linux/macOS 智能启动脚本
├── requirements.txt        # 依赖列表
├── CompressPasswordProbe.spec  # PyInstaller 配置
├── build.py               # 自定义构建脚本
├── config.json            # 配置文件
├── sample_dictionary.txt   # 示例字典文件
├── core/                   # 核心模块
│   ├── __init__.py
│   ├── config.py          # 配置管理
│   ├── archive_handler.py # 压缩文件处理
│   ├── dictionary.py      # 字典处理
│   ├── crack_engine.py    # 破解引擎
│   ├── gpu_accelerator.py # GPU 加速
│   └── logger.py          # 日志管理
├── gui/                    # 图形界面
│   ├── __init__.py
│   ├── main_window_simple.py # 主窗口
│   ├── settings_dialog.py # 设置对话框
│   └── about_dialog.py    # 关于对话框
├── scripts/                # 安装和启动脚本
│   ├── README.md          # 脚本使用说明
│   ├── install.bat        # Windows 虚拟环境安装
│   ├── install.sh         # Linux/macOS 虚拟环境安装
│   ├── install_conda.bat  # Windows Conda 环境安装
│   ├── install_conda.sh   # Linux/macOS Conda 环境安装
│   ├── start_conda.bat    # Windows Conda 环境启动
│   └── start_conda.sh     # Linux/macOS Conda 环境启动
├── lib/                    # 外部工具库
│   └── 7z/                # 7-Zip 工具
├── logs/                   # 日志目录
└── README.md              # 说明文档
```

## 性能优化

### 提高破解速度的建议

1. **使用 GPU 加速**: 在支持的硬件上启用 GPU 加速
2. **调整线程数**: 根据 CPU 核心数调整最大线程数
3. **优化字典**: 使用针对性强的字典文件
4. **批处理大小**: 调整 GPU 批处理大小以平衡性能和内存使用

### 内存使用优化

1. **分批读取**: 程序自动分批读取大型字典文件
2. **及时释放**: 自动管理文件句柄和内存资源
3. **限制尝试次数**: 设置最大尝试次数以控制资源使用

## 故障排除

### 常见问题

1. **GPU 加速不可用**
   - 检查 GPU 驱动程序是否正确安装
   - 验证 CUDA 或 OpenCL 环境配置
   - 查看设置中的 GPU 信息

2. **文件格式不支持**
   - 确保压缩文件格式为 ZIP、7Z 或 RAR
   - 检查文件是否损坏

3. **字典文件读取失败**
   - 确保字典文件为 UTF-8 编码的文本文件
   - 检查文件权限

4. **程序运行缓慢**
   - 尝试禁用 GPU 加速使用 CPU 模式
   - 减少字典文件大小
   - 调整线程数设置

### 日志分析

程序会自动生成详细的日志文件，位于 `logs/` 目录下。通过查看日志可以：

- 了解程序运行状态
- 诊断错误原因
- 分析性能表现

## 开发说明

### 开发环境搭建

1. **克隆项目**

```bash
git clone https://github.com/ZhongYanZhiShi/CompressPasswordProbe.git
cd CompressPasswordProbe
```

2. **创建虚拟环境**

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows
```

3. **安装开发依赖**

```bash
pip install -r requirements.txt
```

### 打包发布

使用 PyInstaller 打包为可执行文件：

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包
pyinstaller CompressPasswordProbe.spec
```

生成的可执行文件位于 `dist/` 目录下。

### 代码结构说明

- **模块化设计**: 核心功能和 GUI 分离
- **异步处理**: 使用 QThread 进行后台处理
- **信号机制**: 使用 Qt 信号槽进行组件通信
- **错误处理**: 完善的异常处理和错误恢复机制

## 贡献指南

欢迎提交 Issue 和 Pull Request！

### 提交 Bug 报告

- 描述复现步骤
- 提供系统信息
- 包含相关日志文件

### 功能建议

- 说明功能需求
- 解释使用场景
- 提供设计建议

### 代码贡献

- Fork 项目
- 创建功能分支
- 编写测试代码
- 提交 Pull Request

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 免责声明

本工具仅供学习和合法用途使用。请勿用于非法破解他人的加密文件。使用者应当遵守当地法律法规，对使用本工具产生的任何后果承担责任。

## 致谢

感谢以下开源项目的贡献：

- Qt/PySide6 团队
- py7zr 开发者
- rarfile 开发者
- CUDA 和 OpenCL 社区
