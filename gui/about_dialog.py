"""
关于对话框
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QTabWidget,
    QWidget,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from core.gpu_accelerator import GPUManager
import sys
import platform


class AboutDialog(QDialog):
    """关于对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于 CompressPasswordProbe")
        self.setModal(True)
        self.resize(500, 400)

        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 创建选项卡
        tab_widget = QTabWidget()

        # 关于选项卡
        about_tab = self.create_about_tab()
        tab_widget.addTab(about_tab, "关于")

        # 系统信息选项卡
        system_tab = self.create_system_tab()
        tab_widget.addTab(system_tab, "系统信息")

        # 许可证选项卡
        license_tab = self.create_license_tab()
        tab_widget.addTab(license_tab, "许可证")

        layout.addWidget(tab_widget)

        # 确定按钮
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

    def create_about_tab(self) -> QWidget:
        """创建关于选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 应用程序信息
        app_info = QLabel()
        app_info.setAlignment(Qt.AlignCenter)
        app_info.setText(
            """
        <h2>CompressPasswordProbe</h2>
        <h3>压缩文件密码破解工具</h3>
        <p><b>版本:</b> 1.0.0</p>
        <p><b>作者:</b> ZhongYanZhiShi</p>
        <p><b>开发时间:</b> 2024年</p>
        """
        )
        layout.addWidget(app_info)

        # 功能特性
        features = QLabel()
        features.setText(
            """
        <h4>主要功能:</h4>
        <ul>
        <li>支持 ZIP、7Z、RAR 格式压缩文件</li>
        <li>字典攻击密码破解</li>
        <li>拖放文件加载</li>
        <li>GPU 加速支持（可选）</li>
        <li>实时进度显示</li>
        <li>多线程处理</li>
        <li>日志记录</li>
        </ul>
        """
        )
        layout.addWidget(features)

        # 技术栈
        tech_stack = QLabel()
        tech_stack.setText(
            """
        <h4>技术栈:</h4>
        <ul>
        <li>Python 3</li>
        <li>PySide6 (Qt for Python)</li>
        <li>py7zr (7Z 支持)</li>
        <li>rarfile (RAR 支持)</li>
        <li>PyCUDA / PyOpenCL (GPU 加速)</li>
        </ul>
        """
        )
        layout.addWidget(tech_stack)

        layout.addStretch()
        return widget

    def create_system_tab(self) -> QWidget:
        """创建系统信息选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        system_info = QTextEdit()
        system_info.setReadOnly(True)

        # 收集系统信息
        info_text = self.get_system_info()
        system_info.setPlainText(info_text)

        layout.addWidget(system_info)
        return widget

    def create_license_tab(self) -> QWidget:
        """创建许可证选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        license_text = QTextEdit()
        license_text.setReadOnly(True)
        license_text.setPlainText(
            """
MIT License

Copyright (c) 2024 ZhongYanZhiShi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

第三方库许可证:
- PySide6: LGPL v3
- py7zr: LGPL v2.1+
- rarfile: ISC License
- PyCUDA: MIT License
- PyOpenCL: MIT License
        """
        )

        layout.addWidget(license_text)
        return widget

    def get_system_info(self) -> str:
        """获取系统信息"""
        gpu_manager = GPUManager()
        system_info = GPUManager.get_system_info()

        info_lines = [
            "系统信息",
            "=" * 50,
            f"操作系统: {platform.platform()}",
            f"处理器: {platform.processor()}",
            f"架构: {platform.architecture()[0]}",
            f"Python 版本: {sys.version}",
            "",
            "GPU 支持",
            "=" * 50,
            f"CUDA 可用: {'是' if system_info.get('cuda_available', False) else '否'}",
            f"OpenCL 可用: {'是' if system_info.get('opencl_available', False) else '否'}",
            f"Numba CUDA 可用: {'是' if system_info.get('numba_cuda_available', False) else '否'}",
            f"NVIDIA 驱动: {'是' if system_info.get('nvidia_driver', False) else '否'}",
            "",
            "当前 GPU 状态",
            "=" * 50,
        ]

        if gpu_manager.is_gpu_available():
            gpu_info = gpu_manager.get_gpu_info()
            info_lines.extend(
                [
                    f"GPU 设备: 可用",
                    f"设备名称: {gpu_info.get('name', '未知')}",
                    f"设备类型: {gpu_info.get('type', '未知')}",
                ]
            )

            if "total_memory" in gpu_info:
                memory_gb = gpu_info["total_memory"] / (1024**3)
                info_lines.append(f"显存: {memory_gb:.1f} GB")

            if "compute_capability" in gpu_info:
                info_lines.append(f"计算能力: {gpu_info['compute_capability']}")

            if "multiprocessor_count" in gpu_info:
                info_lines.append(f"多处理器数量: {gpu_info['multiprocessor_count']}")
        else:
            info_lines.append("GPU 设备: 不可用")

        info_lines.extend(
            [
                "",
                "已安装的 Python 包",
                "=" * 50,
            ]
        )

        # 检查重要包的版本
        packages = [
            "PySide6",
            "py7zr",
            "rarfile",
            "pycuda",
            "pyopencl",
            "numba",
            "psutil",
        ]

        for package in packages:
            try:
                if package == "PySide6":
                    import PySide6

                    version = PySide6.__version__
                elif package == "py7zr":
                    import py7zr

                    version = py7zr.__version__
                elif package == "rarfile":
                    import rarfile

                    version = getattr(rarfile, "__version__", "未知")
                elif package == "pycuda":
                    import pycuda

                    version = pycuda.VERSION_TEXT
                elif package == "pyopencl":
                    import pyopencl

                    version = pyopencl.VERSION_TEXT
                elif package == "numba":
                    import numba

                    version = numba.__version__
                elif package == "psutil":
                    import psutil

                    version = psutil.__version__
                else:
                    version = "未知"

                info_lines.append(f"{package}: {version}")
            except ImportError:
                info_lines.append(f"{package}: 未安装")
            except Exception as e:
                info_lines.append(f"{package}: 错误 ({str(e)})")

        return "\n".join(info_lines)
