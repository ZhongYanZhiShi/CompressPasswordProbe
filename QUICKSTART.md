# 快速开始指南

## 🚀 超简单开始（30秒启动）

### 第一步：下载项目
```bash
git clone https://github.com/ZhongYanZhiShi/CompressPasswordProbe.git
cd CompressPasswordProbe
```

### 第二步：运行启动脚本

**Windows:**
```batch
start.bat
```

**Linux/macOS:**
```bash
chmod +x start.sh && ./start.sh
```

**完成！** 脚本会自动处理一切：
- ✅ 检测环境
- ✅ 安装依赖（如需要）  
- ✅ 启动程序

---

## 🔧 详细安装选项（高级用户）

如果您想要更多控制，可以选择特定的安装方式：

### Windows 用户

#### 方法1: 虚拟环境（传统）
```batch
# 运行安装脚本
install.bat

# 启动程序
start.bat
```

#### 方法2: Conda环境（推荐）
```batch
# 运行Conda安装脚本
install_conda.bat

# 启动程序
start_conda.bat
```

#### 方法3: 手动安装
```batch
# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

### Linux/macOS 用户

#### 方法1: 虚拟环境（传统）
```bash
# 给脚本执行权限
chmod +x install.sh start.sh

# 运行安装脚本
./install.sh

# 启动程序
./start.sh
```

#### 方法2: Conda环境（推荐）
```bash
# 给脚本执行权限
chmod +x install_conda.sh start_conda.sh

# 运行Conda安装脚本
./install_conda.sh

# 启动程序
./start_conda.sh
```

#### 方法3: 手动安装
```bash
# 安装依赖
pip3 install -r requirements.txt

# 运行程序
python3 main.py
```

### 📖 详细说明

- **虚拟环境**: 传统的Python虚拟环境，轻量级
- **Conda环境**: 更强大的包管理，推荐用于科学计算
- **智能启动**: `start.bat` 现在可以自动检测并使用可用的环境

详细的Conda使用指南请参考 [CONDA_GUIDE.md](CONDA_GUIDE.md)

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
