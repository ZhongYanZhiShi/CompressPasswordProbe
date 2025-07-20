"""
主窗口模块 - 简化版本
"""

import os
import sys
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QProgressBar,
    QGroupBox,
    QCheckBox,
    QFileDialog,
    QMessageBox,
    QFrame,
    QApplication,
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QTextCursor

from core.config import Config
from core.archive_handler import ArchiveManager
from core.dictionary import DictionaryReader, DictionaryManager
from core.crack_engine import PasswordCrackEngine
from core.gpu_accelerator import GPUManager
from core.logger import get_logger


class DropArea(QFrame):
    """拖放区域组件"""

    file_dropped = Signal(str)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.setLineWidth(2)
        self.setMinimumHeight(100)

        layout = QVBoxLayout()
        self.label = QLabel("拖放压缩文件到此处\n支持格式: ZIP, 7Z, RAR")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.file_dropped.emit(file_path)


class MainWindow(QMainWindow):
    """主窗口类"""

    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.archive_manager = ArchiveManager()
        self.crack_engine = PasswordCrackEngine(config.config)
        self.gpu_manager = GPUManager()
        self.logger = get_logger()

        self.current_archive_path = ""
        self.current_dictionary_path = ""

        self.setWindowTitle("CompressPasswordProbe - 压缩文件密码破解工具")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)

        self.init_ui()
        self.connect_signals()
        self.load_last_paths()
        self.check_gpu_status()

    def init_ui(self):
        """初始化用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # 文件选择区域
        file_group = self.create_file_selection_group()
        main_layout.addWidget(file_group)

        # 控制区域
        control_group = self.create_control_group()
        main_layout.addWidget(control_group)

        # 进度区域
        progress_group = self.create_progress_group()
        main_layout.addWidget(progress_group)

        # 日志区域（可拉伸）
        log_group = self.create_log_group()
        main_layout.addWidget(log_group, 1)  # 设置拉伸因子为1，使其可以拉伸

        self.statusBar().showMessage("就绪")

    def create_file_selection_group(self) -> QGroupBox:
        """创建文件选择组"""
        group = QGroupBox("文件选择")
        layout = QVBoxLayout(group)

        # 压缩文件选择
        archive_layout = QHBoxLayout()
        archive_layout.addWidget(QLabel("压缩文件:"))
        self.archive_path_edit = QLineEdit()
        self.archive_path_edit.setReadOnly(True)
        self.archive_browse_btn = QPushButton("浏览...")
        self.archive_browse_btn.clicked.connect(self.browse_archive_file)

        archive_layout.addWidget(self.archive_path_edit)
        archive_layout.addWidget(self.archive_browse_btn)
        layout.addLayout(archive_layout)

        # 拖放区域
        self.drop_area = DropArea()
        self.drop_area.file_dropped.connect(self.load_archive_file)
        layout.addWidget(self.drop_area)

        # 字典文件选择
        dict_layout = QHBoxLayout()
        dict_layout.addWidget(QLabel("字典文件:"))
        self.dict_path_edit = QLineEdit()
        self.dict_path_edit.setReadOnly(True)
        self.dict_browse_btn = QPushButton("浏览...")
        self.dict_browse_btn.clicked.connect(self.browse_dictionary_file)
        self.create_sample_dict_btn = QPushButton("创建示例字典")
        self.create_sample_dict_btn.clicked.connect(self.create_sample_dictionary)

        dict_layout.addWidget(self.dict_path_edit)
        dict_layout.addWidget(self.dict_browse_btn)
        dict_layout.addWidget(self.create_sample_dict_btn)
        layout.addLayout(dict_layout)

        return group

    def create_control_group(self) -> QGroupBox:
        """创建控制组"""
        group = QGroupBox("控制选项")
        layout = QGridLayout(group)

        # GPU加速选项
        self.gpu_checkbox = QCheckBox("启用GPU加速")
        self.gpu_checkbox.setChecked(self.config.get("gpu_acceleration", False))
        self.gpu_status_label = QLabel("GPU状态: 检测中...")
        layout.addWidget(self.gpu_checkbox, 0, 0)
        layout.addWidget(self.gpu_status_label, 0, 1)

        # 控制按钮
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("开始破解")
        self.start_btn.clicked.connect(self.start_crack)

        self.pause_btn = QPushButton("暂停")
        self.pause_btn.clicked.connect(self.pause_crack)
        self.pause_btn.setEnabled(False)

        self.stop_btn = QPushButton("停止")
        self.stop_btn.clicked.connect(self.stop_crack)
        self.stop_btn.setEnabled(False)

        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.pause_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout, 1, 0, 1, 2)

        return group

    def create_progress_group(self) -> QGroupBox:
        """创建进度组"""
        group = QGroupBox("破解进度")
        layout = QVBoxLayout(group)

        # 进度信息
        info_layout = QGridLayout()
        info_layout.addWidget(QLabel("当前密码:"), 0, 0)
        self.current_password_label = QLabel("-")
        info_layout.addWidget(self.current_password_label, 0, 1)

        info_layout.addWidget(QLabel("进度:"), 1, 0)
        self.progress_label = QLabel("0 / 0")
        info_layout.addWidget(self.progress_label, 1, 1)

        info_layout.addWidget(QLabel("速度:"), 2, 0)
        self.speed_label = QLabel("0 passwords/sec")
        info_layout.addWidget(self.speed_label, 2, 1)

        layout.addLayout(info_layout)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        # 找到的密码区域
        found_password_layout = QHBoxLayout()
        found_password_layout.addWidget(QLabel("找到的密码:"))
        self.found_password_edit = QLineEdit()
        self.found_password_edit.setReadOnly(True)
        self.found_password_edit.setPlaceholderText("密码破解成功后将显示在这里")
        self.copy_password_btn = QPushButton("复制密码")
        self.copy_password_btn.clicked.connect(self.copy_found_password)
        self.copy_password_btn.setEnabled(False)

        found_password_layout.addWidget(self.found_password_edit)
        found_password_layout.addWidget(self.copy_password_btn)
        layout.addLayout(found_password_layout)

        return group

    def create_log_group(self) -> QGroupBox:
        """创建日志组"""
        group = QGroupBox("日志输出")
        layout = QVBoxLayout(group)

        # 日志文本区域
        self.log_text = QTextEdit()
        self.log_text.setMinimumHeight(100)  # 设置最小高度
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        return group

    def connect_signals(self):
        """连接信号"""
        self.crack_engine.progress_updated.connect(self.update_progress)
        self.crack_engine.password_found.connect(self.on_password_found)
        self.crack_engine.crack_finished.connect(self.on_crack_finished)
        self.crack_engine.speed_updated.connect(self.update_speed)

        self.gpu_checkbox.stateChanged.connect(self.on_gpu_setting_changed)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_elapsed_time)
        self.start_time = 0

    def browse_archive_file(self):
        """浏览压缩文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择压缩文件",
            self.config.get("last_archive_path", ""),
            self.archive_manager.get_supported_formats_filter(),
        )

        if file_path:
            self.load_archive_file(file_path)

    def load_archive_file(self, file_path: str):
        """加载压缩文件"""
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "错误", "文件不存在")
            return

        if not self.archive_manager.is_supported(file_path):
            QMessageBox.warning(self, "错误", "不支持的文件格式")
            return

        self.current_archive_path = file_path
        self.archive_path_edit.setText(file_path)
        self.config.set("last_archive_path", file_path)
        self.config.save_config()

        info = self.archive_manager.get_archive_info(file_path)
        if "error" not in info:
            self.log_message(f"已加载压缩文件: {os.path.basename(file_path)}")
            self.log_message(f"格式: {info.get('format', '未知')}")
            self.log_message(f"文件数量: {info.get('file_count', 0)}")
            self.log_message(
                f"是否加密: {'是' if info.get('has_password', False) else '否'}"
            )
        else:
            self.log_message(f"加载文件失败: {info['error']}")

    def browse_dictionary_file(self):
        """浏览字典文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择字典文件",
            self.config.get("last_dictionary_path", ""),
            "文本文件 (*.txt);;所有文件 (*.*)",
        )

        if file_path:
            self.load_dictionary_file(file_path)

    def load_dictionary_file(self, file_path: str):
        """加载字典文件"""
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "错误", "字典文件不存在")
            return

        self.current_dictionary_path = file_path
        self.dict_path_edit.setText(file_path)
        self.config.set("last_dictionary_path", file_path)
        self.config.save_config()

        dictionary_reader = DictionaryReader(file_path)
        validation_result = dictionary_reader.validate_dictionary()

        if validation_result["valid"]:
            self.log_message(f"已加载字典文件: {os.path.basename(file_path)}")
            self.log_message(f"密码数量: {validation_result['password_count']}")
        else:
            self.log_message(f"字典文件验证失败: {validation_result['error']}")
            QMessageBox.warning(
                self, "错误", f"字典文件无效: {validation_result['error']}"
            )

    def create_sample_dictionary(self):
        """创建示例字典"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存示例字典", "sample_dictionary.txt", "文本文件 (*.txt)"
        )

        if file_path:
            passwords = DictionaryManager.get_common_passwords()
            if DictionaryManager.create_sample_dictionary(file_path, passwords):
                QMessageBox.information(self, "成功", f"示例字典已创建: {file_path}")
                self.load_dictionary_file(file_path)
            else:
                QMessageBox.warning(self, "错误", "创建示例字典失败")

    def start_crack(self):
        """开始破解"""
        if not self.current_archive_path:
            QMessageBox.warning(self, "错误", "请先选择压缩文件")
            return

        if not self.current_dictionary_path:
            QMessageBox.warning(self, "错误", "请先选择字典文件")
            return

        self.config.set("gpu_acceleration", self.gpu_checkbox.isChecked())
        self.config.save_config()

        if self.crack_engine.start_crack(
            self.current_archive_path, self.current_dictionary_path
        ):
            self.start_btn.setEnabled(False)
            self.pause_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)

            self.log_message("开始密码破解...")
            self.statusBar().showMessage("正在破解...")

            import time

            self.start_time = time.time()
            self.timer.start(1000)
        else:
            QMessageBox.warning(self, "错误", "启动破解失败")

    def pause_crack(self):
        """暂停破解"""
        if self.crack_engine.is_running():
            if self.crack_engine.is_paused():
                self.crack_engine.resume_crack()
                self.pause_btn.setText("暂停")
                self.timer.start(1000)
                self.log_message("恢复密码破解")
            else:
                self.crack_engine.pause_crack()
                self.pause_btn.setText("恢复")
                self.timer.stop()
                self.log_message("暂停密码破解")

    def stop_crack(self):
        """停止破解"""
        self.crack_engine.stop_crack()
        self.reset_ui_state()
        self.log_message("停止密码破解")

    def reset_ui_state(self):
        """重置UI状态"""
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("暂停")
        self.stop_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.current_password_label.setText("-")
        self.progress_label.setText("0 / 0")
        self.speed_label.setText("0 passwords/sec")
        self.found_password_edit.clear()
        self.copy_password_btn.setEnabled(False)
        self.timer.stop()
        self.statusBar().showMessage("就绪")

    def update_progress(self, current: int, total: int, password: str):
        """更新进度"""
        self.current_password_label.setText(password)
        self.progress_label.setText(f"{current} / {total}")

        if total > 0:
            progress = int((current / total) * 100)
            self.progress_bar.setValue(progress)

    def update_speed(self, speed: float):
        """更新速度"""
        self.speed_label.setText(f"{speed:.1f} passwords/sec")

    def update_elapsed_time(self):
        """更新耗时"""
        if self.start_time > 0:
            import time

            elapsed = int(time.time() - self.start_time)
            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            seconds = elapsed % 60
            # 可以添加时间显示标签

    def on_password_found(self, password: str, attempts: int, elapsed_time: float):
        """密码找到回调"""
        self.log_message(f"密码破解成功!")
        self.log_message(f"密码: {password}")
        self.log_message(f"尝试次数: {attempts}")
        self.log_message(f"耗时: {elapsed_time:.2f} 秒")

        # 在找到密码文本框中显示密码并启用复制按钮
        self.found_password_edit.setText(password)
        self.copy_password_btn.setEnabled(True)

        # 创建自定义消息框，包含复制按钮
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("破解成功")
        msg_box.setText(
            f"找到密码: {password}\n\n"
            f"尝试次数: {attempts}\n"
            f"耗时: {elapsed_time:.2f} 秒"
        )
        msg_box.setIcon(QMessageBox.Information)

        # 添加复制按钮
        copy_button = msg_box.addButton("复制密码", QMessageBox.ActionRole)
        ok_button = msg_box.addButton(QMessageBox.Ok)

        msg_box.exec()

        # 检查用户点击的按钮
        if msg_box.clickedButton() == copy_button:
            self.copy_password_to_clipboard(password)

    def copy_password_to_clipboard(self, password: str):
        """复制密码到剪贴板"""
        clipboard = QApplication.clipboard()
        clipboard.setText(password)

        # 显示复制成功的提示
        self.log_message(f"密码已复制到剪贴板: {password}")
        self.statusBar().showMessage("密码已复制到剪贴板", 3000)  # 显示3秒

        # 可选：显示简短的提示消息
        QMessageBox.information(self, "复制成功", f"密码 '{password}' 已复制到剪贴板")

    def copy_found_password(self):
        """复制找到的密码到剪贴板"""
        password = self.found_password_edit.text()
        if password:
            clipboard = QApplication.clipboard()
            clipboard.setText(password)

            self.log_message(f"密码已复制到剪贴板: {password}")
            self.statusBar().showMessage("密码已复制到剪贴板", 3000)  # 显示3秒

    def on_crack_finished(self, success: bool, error_message: str):
        """破解完成回调"""
        self.reset_ui_state()

        if not success and error_message:
            self.log_message(f"破解失败: {error_message}")
            if error_message != "未找到正确的密码":
                QMessageBox.warning(self, "破解失败", error_message)
        elif not success:
            self.log_message("破解完成，未找到正确的密码")

    def on_gpu_setting_changed(self, state: int):
        """GPU设置变化"""
        self.config.set("gpu_acceleration", state == Qt.Checked)

    def check_gpu_status(self):
        """检查GPU状态"""
        if self.gpu_manager.is_gpu_available():
            gpu_info = self.gpu_manager.get_gpu_info()
            gpu_name = gpu_info.get("name", "未知GPU")
            self.gpu_status_label.setText(f"GPU状态: 可用 ({gpu_name})")
            self.gpu_checkbox.setEnabled(True)
        else:
            self.gpu_status_label.setText("GPU状态: 不可用")
            self.gpu_checkbox.setEnabled(False)
            self.gpu_checkbox.setChecked(False)

    def load_last_paths(self):
        """加载上次的文件路径"""
        last_archive = self.config.get("last_archive_path", "")
        last_dict = self.config.get("last_dictionary_path", "")

        if last_archive and os.path.exists(last_archive):
            self.load_archive_file(last_archive)

        if last_dict and os.path.exists(last_dict):
            self.load_dictionary_file(last_dict)

    def log_message(self, message: str):
        """添加日志消息"""
        import datetime

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"

        self.log_text.append(formatted_message)
        self.logger.info(message)

        # 自动滚动到底部
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)
