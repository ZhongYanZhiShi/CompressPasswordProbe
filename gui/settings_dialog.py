"""
设置对话框
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QSpinBox,
    QCheckBox,
    QPushButton,
    QGroupBox,
    QLineEdit,
    QFileDialog,
    QTabWidget,
    QWidget,
    QTextEdit,
    QComboBox,
)
from PySide6.QtCore import Qt
from core.config import Config
from core.gpu_accelerator import GPUManager


class SettingsDialog(QDialog):
    """设置对话框"""

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.gpu_manager = GPUManager()

        self.setWindowTitle("设置")
        self.setModal(True)
        self.resize(500, 400)

        self.init_ui()
        self.load_settings()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 创建选项卡
        tab_widget = QTabWidget()

        # 常规设置选项卡
        general_tab = self.create_general_tab()
        tab_widget.addTab(general_tab, "常规")

        # 性能设置选项卡
        performance_tab = self.create_performance_tab()
        tab_widget.addTab(performance_tab, "性能")

        # GPU设置选项卡
        gpu_tab = self.create_gpu_tab()
        tab_widget.addTab(gpu_tab, "GPU")

        # 日志设置选项卡
        log_tab = self.create_log_tab()
        tab_widget.addTab(log_tab, "日志")

        layout.addWidget(tab_widget)

        # 按钮
        button_layout = QHBoxLayout()

        self.ok_btn = QPushButton("确定")
        self.ok_btn.clicked.connect(self.accept)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)

        self.apply_btn = QPushButton("应用")
        self.apply_btn.clicked.connect(self.apply_settings)

        self.reset_btn = QPushButton("重置")
        self.reset_btn.clicked.connect(self.reset_settings)

        button_layout.addStretch()
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.ok_btn)

        layout.addLayout(button_layout)

    def create_general_tab(self) -> QWidget:
        """创建常规设置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 基本设置组
        basic_group = QGroupBox("基本设置")
        basic_layout = QGridLayout(basic_group)

        # 最大尝试次数
        basic_layout.addWidget(QLabel("最大尝试次数:"), 0, 0)
        self.max_attempts_spin = QSpinBox()
        self.max_attempts_spin.setRange(0, 999999999)
        self.max_attempts_spin.setSpecialValueText("无限制")
        basic_layout.addWidget(self.max_attempts_spin, 0, 1)

        # 超时时间
        basic_layout.addWidget(QLabel("超时时间(秒):"), 1, 0)
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(0, 86400)  # 最多24小时
        self.timeout_spin.setSpecialValueText("无限制")
        basic_layout.addWidget(self.timeout_spin, 1, 1)

        # 语言设置
        basic_layout.addWidget(QLabel("界面语言:"), 2, 0)
        self.language_combo = QComboBox()
        self.language_combo.addItems(["中文(简体)", "English"])
        basic_layout.addWidget(self.language_combo, 2, 1)

        layout.addWidget(basic_group)

        # 文件设置组
        file_group = QGroupBox("文件设置")
        file_layout = QGridLayout(file_group)

        # 自动保存路径
        self.auto_save_paths_cb = QCheckBox("自动保存文件路径")
        file_layout.addWidget(self.auto_save_paths_cb, 0, 0, 1, 2)

        layout.addWidget(file_group)

        layout.addStretch()
        return widget

    def create_performance_tab(self) -> QWidget:
        """创建性能设置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 线程设置组
        thread_group = QGroupBox("线程设置")
        thread_layout = QGridLayout(thread_group)

        thread_layout.addWidget(QLabel("最大线程数:"), 0, 0)
        self.max_threads_spin = QSpinBox()
        self.max_threads_spin.setRange(1, 32)
        thread_layout.addWidget(self.max_threads_spin, 0, 1)

        layout.addWidget(thread_group)

        # 批处理设置组
        batch_group = QGroupBox("批处理设置")
        batch_layout = QGridLayout(batch_group)

        batch_layout.addWidget(QLabel("批处理大小:"), 0, 0)
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setRange(100, 10000)
        batch_layout.addWidget(self.batch_size_spin, 0, 1)

        layout.addWidget(batch_group)

        layout.addStretch()
        return widget

    def create_gpu_tab(self) -> QWidget:
        """创建GPU设置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # GPU设置组
        gpu_group = QGroupBox("GPU设置")
        gpu_layout = QGridLayout(gpu_group)

        # GPU加速开关
        self.gpu_acceleration_cb = QCheckBox("启用GPU加速")
        gpu_layout.addWidget(self.gpu_acceleration_cb, 0, 0, 1, 2)

        # 自动检测GPU
        self.auto_detect_gpu_cb = QCheckBox("自动检测GPU")
        gpu_layout.addWidget(self.auto_detect_gpu_cb, 1, 0, 1, 2)

        layout.addWidget(gpu_group)

        # GPU信息组
        info_group = QGroupBox("GPU信息")
        info_layout = QVBoxLayout(info_group)

        self.gpu_info_text = QTextEdit()
        self.gpu_info_text.setReadOnly(True)
        self.gpu_info_text.setMaximumHeight(150)
        info_layout.addWidget(self.gpu_info_text)

        # 刷新GPU信息按钮
        refresh_btn = QPushButton("刷新GPU信息")
        refresh_btn.clicked.connect(self.refresh_gpu_info)
        info_layout.addWidget(refresh_btn)

        layout.addWidget(info_group)

        # 加载GPU信息
        self.refresh_gpu_info()

        layout.addStretch()
        return widget

    def create_log_tab(self) -> QWidget:
        """创建日志设置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 日志设置组
        log_group = QGroupBox("日志设置")
        log_layout = QGridLayout(log_group)

        # 保存日志
        self.save_log_cb = QCheckBox("保存日志到文件")
        log_layout.addWidget(self.save_log_cb, 0, 0, 1, 2)

        # 日志目录
        log_layout.addWidget(QLabel("日志目录:"), 1, 0)
        self.log_directory_edit = QLineEdit()
        self.log_directory_browse_btn = QPushButton("浏览...")
        self.log_directory_browse_btn.clicked.connect(self.browse_log_directory)

        log_dir_layout = QHBoxLayout()
        log_dir_layout.addWidget(self.log_directory_edit)
        log_dir_layout.addWidget(self.log_directory_browse_btn)
        log_layout.addLayout(log_dir_layout, 1, 1)

        layout.addWidget(log_group)

        layout.addStretch()
        return widget

    def load_settings(self):
        """加载设置"""
        # 常规设置
        self.max_attempts_spin.setValue(self.config.get("max_attempts", 0))
        self.timeout_spin.setValue(self.config.get("timeout_seconds", 0))

        language = self.config.get("ui_language", "zh_CN")
        if language == "zh_CN":
            self.language_combo.setCurrentIndex(0)
        else:
            self.language_combo.setCurrentIndex(1)

        # 性能设置
        self.max_threads_spin.setValue(self.config.get("max_threads", 4))
        self.batch_size_spin.setValue(self.config.get("batch_size", 1000))

        # GPU设置
        self.gpu_acceleration_cb.setChecked(self.config.get("gpu_acceleration", False))
        self.auto_detect_gpu_cb.setChecked(self.config.get("auto_detect_gpu", True))

        # 日志设置
        self.save_log_cb.setChecked(self.config.get("save_log", True))
        self.log_directory_edit.setText(self.config.get("log_directory", "logs"))

    def apply_settings(self):
        """应用设置"""
        # 常规设置
        self.config.set("max_attempts", self.max_attempts_spin.value())
        self.config.set("timeout_seconds", self.timeout_spin.value())

        language = "zh_CN" if self.language_combo.currentIndex() == 0 else "en_US"
        self.config.set("ui_language", language)

        # 性能设置
        self.config.set("max_threads", self.max_threads_spin.value())
        self.config.set("batch_size", self.batch_size_spin.value())

        # GPU设置
        self.config.set("gpu_acceleration", self.gpu_acceleration_cb.isChecked())
        self.config.set("auto_detect_gpu", self.auto_detect_gpu_cb.isChecked())

        # 日志设置
        self.config.set("save_log", self.save_log_cb.isChecked())
        self.config.set("log_directory", self.log_directory_edit.text())

        # 保存配置
        self.config.save_config()

    def reset_settings(self):
        """重置设置"""
        self.config.reset_to_default()
        self.load_settings()

    def refresh_gpu_info(self):
        """刷新GPU信息"""
        info_text = "GPU检测结果:\n\n"

        if self.gpu_manager.is_gpu_available():
            gpu_info = self.gpu_manager.get_gpu_info()
            info_text += f"状态: 可用\n"
            info_text += f"设备名称: {gpu_info.get('name', '未知')}\n"
            info_text += f"类型: {gpu_info.get('type', '未知')}\n"

            if "compute_capability" in gpu_info:
                info_text += f"计算能力: {gpu_info['compute_capability']}\n"
            if "total_memory" in gpu_info:
                memory_gb = gpu_info["total_memory"] / (1024**3)
                info_text += f"显存: {memory_gb:.1f} GB\n"
            if "multiprocessor_count" in gpu_info:
                info_text += f"多处理器数量: {gpu_info['multiprocessor_count']}\n"
        else:
            info_text += "状态: 不可用\n"
            info_text += "未检测到支持的GPU设备\n\n"

            # 显示系统信息
            system_info = GPUManager.get_system_info()
            info_text += "系统信息:\n"
            info_text += f"CUDA支持: {'是' if system_info.get('cuda_available', False) else '否'}\n"
            info_text += f"OpenCL支持: {'是' if system_info.get('opencl_available', False) else '否'}\n"
            info_text += f"NVIDIA驱动: {'是' if system_info.get('nvidia_driver', False) else '否'}\n"

        self.gpu_info_text.setPlainText(info_text)

    def browse_log_directory(self):
        """浏览日志目录"""
        directory = QFileDialog.getExistingDirectory(
            self, "选择日志目录", self.log_directory_edit.text()
        )

        if directory:
            self.log_directory_edit.setText(directory)

    def accept(self):
        """确定按钮"""
        self.apply_settings()
        super().accept()

    def reject(self):
        """取消按钮"""
        super().reject()
