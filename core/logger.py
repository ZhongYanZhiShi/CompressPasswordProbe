"""
日志记录模块
"""

import os
import logging
import datetime
from typing import Optional


class Logger:
    """日志记录器"""

    def __init__(self, log_directory: str = "logs", log_level: int = logging.INFO):
        self.log_directory = log_directory
        self.log_level = log_level
        self.logger = None
        self._setup_logger()

    def _setup_logger(self):
        """设置日志记录器"""
        # 创建日志目录
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)

        # 创建日志文件名（按日期）
        today = datetime.datetime.now().strftime("%Y%m%d")
        log_filename = f"compress_password_probe_{today}.log"
        log_path = os.path.join(self.log_directory, log_filename)

        # 配置日志记录器
        self.logger = logging.getLogger("CompressPasswordProbe")
        self.logger.setLevel(self.log_level)

        # 清除已存在的处理器
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # 文件处理器
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(self.log_level)

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)

        # 格式化器
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def log(self, message: str, level: int = logging.INFO):
        """记录日志"""
        if self.logger:
            self.logger.log(level, message)

    def info(self, message: str):
        """记录信息日志"""
        self.log(message, logging.INFO)

    def warning(self, message: str):
        """记录警告日志"""
        self.log(message, logging.WARNING)

    def error(self, message: str):
        """记录错误日志"""
        self.log(message, logging.ERROR)

    def debug(self, message: str):
        """记录调试日志"""
        self.log(message, logging.DEBUG)

    def log_crack_session(
        self, archive_path: str, dictionary_path: str, result: Optional[dict] = None
    ):
        """记录破解会话"""
        session_start = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.info("=" * 50)
        self.info(f"破解会话开始: {session_start}")
        self.info(f"压缩文件: {archive_path}")
        self.info(f"字典文件: {dictionary_path}")

        if result:
            self.info(f"破解结果: {'成功' if result.get('success', False) else '失败'}")
            if result.get("success", False):
                self.info(f"找到密码: {result.get('password', '')}")
            self.info(f"尝试次数: {result.get('attempts', 0)}")
            self.info(f"耗时: {result.get('elapsed_time', 0):.2f} 秒")
            if result.get("used_gpu", False):
                self.info("使用了GPU加速")

        self.info("=" * 50)

    def get_log_file_path(self) -> str:
        """获取当前日志文件路径"""
        today = datetime.datetime.now().strftime("%Y%m%d")
        log_filename = f"compress_password_probe_{today}.log"
        return os.path.join(self.log_directory, log_filename)

    def clear_old_logs(self, days_to_keep: int = 30):
        """清理旧日志文件"""
        try:
            if not os.path.exists(self.log_directory):
                return

            cutoff_date = datetime.datetime.now() - datetime.timedelta(
                days=days_to_keep
            )

            for filename in os.listdir(self.log_directory):
                if filename.endswith(".log"):
                    file_path = os.path.join(self.log_directory, filename)
                    file_time = datetime.datetime.fromtimestamp(
                        os.path.getctime(file_path)
                    )

                    if file_time < cutoff_date:
                        os.remove(file_path)
                        self.info(f"删除旧日志文件: {filename}")

        except Exception as e:
            self.error(f"清理旧日志文件失败: {str(e)}")


# 全局日志实例
_global_logger = None


def get_logger() -> Logger:
    """获取全局日志实例"""
    global _global_logger
    if _global_logger is None:
        _global_logger = Logger()
    return _global_logger
