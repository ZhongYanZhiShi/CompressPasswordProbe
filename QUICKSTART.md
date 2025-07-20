# 快速开始指南

## 安装和运行

### Windows 用户

1. **自动安装（推荐）**
   ```bash
   # 运行安装脚本
   install.bat
   
   # 启动程序
   start.bat
   ```

2. **手动安装**
   ```bash
   # 安装依赖
   pip install -r requirements.txt
   
   # 运行程序
   python main.py
   ```

### Linux/macOS 用户

1. **自动安装（推荐）**
   ```bash
   # 给脚本执行权限
   chmod +x install.sh start.sh
   
   # 运行安装脚本
   ./install.sh
   
   # 启动程序
   ./start.sh
   ```

2. **手动安装**
   ```bash
   # 安装依赖
   pip3 install -r requirements.txt
   
   # 运行程序
   python3 main.py
   ```

## 使用流程

1. **选择压缩文件**
   - 点击"浏览..."按钮选择 ZIP/7Z/RAR 文件
   - 或直接拖拽文件到窗口

2. **选择字典文件**
   - 点击"浏览..."选择 .txt 字典文件
   - 或使用"创建示例字典"创建测试字典

3. **开始破解**
   - 检查 GPU 加速选项（如果可用）
   - 点击"开始破解"按钮
   - 观察实时进度

4. **查看结果**
   - 成功时会显示密码
   - 查看日志了解详细信息

## 故障排除

### 常见问题

1. **无法启动程序**
   ```bash
   # 检查 Python 版本
   python --version  # 需要 3.8+
   
   # 测试项目
   python test_project.py
   ```

2. **GPU 加速不可用**
   - 检查 GPU 驱动
   - 安装 CUDA/OpenCL
   - 查看设置中的 GPU 信息

3. **依赖包安装失败**
   ```bash
   # 升级 pip
   python -m pip install --upgrade pip
   
   # 单独安装核心包
   pip install PySide6 py7zr rarfile
   ```

## 性能优化

- 使用 SSD 存储字典文件
- 启用 GPU 加速（如果支持）
- 调整线程数设置
- 使用针对性字典

## 安全提醒

⚠️ 本工具仅供合法用途使用，请勿用于非法破解他人文件。
