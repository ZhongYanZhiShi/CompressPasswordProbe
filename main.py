"""
CompressPasswordProbe - 压缩文件密码破解工具
主入口模块
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication
from gui.main_window_simple import MainWindow
from core.config import Config


def main():
    """应用程序主入口"""
    # 设置应用程序信息
    QCoreApplication.setApplicationName("CompressPasswordProbe")
    QCoreApplication.setApplicationVersion("1.0.0")
    QCoreApplication.setOrganizationName("ZhongYanZhiShi")

    # 创建应用程序实例
    app = QApplication(sys.argv)

    # 初始化配置
    config = Config()

    # 创建主窗口
    main_window = MainWindow(config)
    main_window.show()

    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
