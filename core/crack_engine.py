"""
密码破解引擎
"""

import time
import threading
from typing import Optional, Callable, Dict, Any
from PySide6.QtCore import QObject, Signal, QThread
from .archive_handler import ArchiveManager
from .dictionary import DictionaryReader
from .gpu_accelerator import GPUManager
from .logger import Logger


class PasswordCrackResult:
    """密码破解结果"""

    def __init__(self):
        self.success = False
        self.password = ""
        self.attempts = 0
        self.elapsed_time = 0.0
        self.error_message = ""
        self.used_gpu = False


class PasswordCrackWorker(QThread):
    """密码破解工作线程"""

    # 信号定义
    progress_updated = Signal(int, int, str)  # 当前进度, 总数, 当前密码
    password_found = Signal(str, int, float)  # 找到的密码, 尝试次数, 耗时
    crack_finished = Signal(bool, str)  # 是否成功, 错误信息
    speed_updated = Signal(float)  # 测试速度 (passwords/second)

    def __init__(self, archive_path: str, dictionary_path: str, config: Dict[str, Any]):
        super().__init__()
        self.archive_path = archive_path
        self.dictionary_path = dictionary_path
        self.config = config
        self.archive_manager = ArchiveManager()
        self.gpu_manager = GPUManager()
        self.logger = Logger()

        self.is_running = False
        self.is_paused = False
        self.result = PasswordCrackResult()

        # 性能统计
        self.start_time = 0
        self.last_speed_update = 0
        self.speed_counter = 0

    def run(self):
        """运行密码破解"""
        self.is_running = True
        self.start_time = time.time()
        self.last_speed_update = self.start_time
        self.speed_counter = 0

        try:
            # 验证文件
            if not self.archive_manager.is_supported(self.archive_path):
                self.crack_finished.emit(False, "不支持的压缩文件格式")
                return

            # 初始化字典读取器
            dictionary_reader = DictionaryReader(self.dictionary_path)
            total_passwords = dictionary_reader.get_total_passwords()

            if total_passwords == 0:
                self.crack_finished.emit(False, "字典文件为空或无法读取")
                return

            self.logger.log(f"开始破解: {self.archive_path}")
            self.logger.log(
                f"字典文件: {self.dictionary_path} (共 {total_passwords} 个密码)"
            )

            # 选择处理模式
            use_gpu = (
                self.config.get("gpu_acceleration", False)
                and self.gpu_manager.is_gpu_available()
            )
            batch_size = self.config.get("batch_size", 1000) if use_gpu else 1

            if use_gpu:
                self.logger.log("使用GPU加速模式")
                self._crack_with_gpu(dictionary_reader, total_passwords)
            else:
                self.logger.log("使用CPU模式")
                self._crack_with_cpu(dictionary_reader, total_passwords)

        except Exception as e:
            self.logger.log(f"破解过程中发生错误: {str(e)}")
            self.crack_finished.emit(False, f"破解过程中发生错误: {str(e)}")
        finally:
            self.is_running = False

    def _crack_with_cpu(
        self, dictionary_reader: DictionaryReader, total_passwords: int
    ):
        """使用CPU进行密码破解"""
        attempts = 0
        max_attempts = self.config.get("max_attempts", 0)

        for password in dictionary_reader.read_single_password():
            if not self.is_running:
                break

            # 暂停检查
            while self.is_paused and self.is_running:
                time.sleep(0.1)

            attempts += 1
            self.speed_counter += 1

            # 更新进度和速度
            self.progress_updated.emit(attempts, total_passwords, password)
            self._update_speed()

            # 测试密码
            if self.archive_manager.test_password(self.archive_path, password):
                elapsed_time = time.time() - self.start_time
                self.result.success = True
                self.result.password = password
                self.result.attempts = attempts
                self.result.elapsed_time = elapsed_time

                self.logger.log(
                    f"密码破解成功: {password} (尝试 {attempts} 次, 耗时 {elapsed_time:.2f} 秒)"
                )
                self.password_found.emit(password, attempts, elapsed_time)
                self.crack_finished.emit(True, "")
                return

            # 检查最大尝试次数限制
            if max_attempts > 0 and attempts >= max_attempts:
                self.logger.log(f"达到最大尝试次数限制: {max_attempts}")
                break

        # 未找到密码
        elapsed_time = time.time() - self.start_time
        self.result.attempts = attempts
        self.result.elapsed_time = elapsed_time

        self.logger.log(
            f"密码破解失败 (尝试 {attempts} 次, 耗时 {elapsed_time:.2f} 秒)"
        )
        self.crack_finished.emit(False, "未找到正确的密码")

    def _crack_with_gpu(
        self, dictionary_reader: DictionaryReader, total_passwords: int
    ):
        """使用GPU进行密码破解（批处理模式）"""
        attempts = 0
        max_attempts = self.config.get("max_attempts", 0)
        batch_size = self.config.get("batch_size", 1000)

        for password_batch in dictionary_reader.read_passwords(batch_size):
            if not self.is_running:
                break

            # 暂停检查
            while self.is_paused and self.is_running:
                time.sleep(0.1)

            attempts += len(password_batch)
            self.speed_counter += len(password_batch)

            # 更新进度
            current_password = password_batch[0] if password_batch else ""
            self.progress_updated.emit(attempts, total_passwords, current_password)
            self._update_speed()

            # 首先尝试GPU加速
            found_password = self.gpu_manager.test_passwords_with_gpu(
                password_batch,
                lambda pwd: self.archive_manager.test_password(self.archive_path, pwd),
            )

            if found_password:
                elapsed_time = time.time() - self.start_time
                self.result.success = True
                self.result.password = found_password
                self.result.attempts = attempts
                self.result.elapsed_time = elapsed_time
                self.result.used_gpu = True

                self.logger.log(
                    f"密码破解成功 (GPU): {found_password} (尝试 {attempts} 次, 耗时 {elapsed_time:.2f} 秒)"
                )
                self.password_found.emit(found_password, attempts, elapsed_time)
                self.crack_finished.emit(True, "")
                return

            # GPU未找到，回退到CPU逐个测试这个批次
            for password in password_batch:
                if not self.is_running:
                    break

                if self.archive_manager.test_password(self.archive_path, password):
                    elapsed_time = time.time() - self.start_time
                    self.result.success = True
                    self.result.password = password
                    self.result.attempts = attempts
                    self.result.elapsed_time = elapsed_time

                    self.logger.log(
                        f"密码破解成功 (CPU回退): {password} (尝试 {attempts} 次, 耗时 {elapsed_time:.2f} 秒)"
                    )
                    self.password_found.emit(password, attempts, elapsed_time)
                    self.crack_finished.emit(True, "")
                    return

            # 检查最大尝试次数限制
            if max_attempts > 0 and attempts >= max_attempts:
                self.logger.log(f"达到最大尝试次数限制: {max_attempts}")
                break

        # 未找到密码
        elapsed_time = time.time() - self.start_time
        self.result.attempts = attempts
        self.result.elapsed_time = elapsed_time

        self.logger.log(
            f"密码破解失败 (尝试 {attempts} 次, 耗时 {elapsed_time:.2f} 秒)"
        )
        self.crack_finished.emit(False, "未找到正确的密码")

    def _update_speed(self):
        """更新测试速度"""
        current_time = time.time()
        if current_time - self.last_speed_update >= 1.0:  # 每秒更新一次
            speed = self.speed_counter / (current_time - self.last_speed_update)
            self.speed_updated.emit(speed)
            self.last_speed_update = current_time
            self.speed_counter = 0

    def pause(self):
        """暂停破解"""
        self.is_paused = True
        self.logger.log("密码破解已暂停")

    def resume(self):
        """恢复破解"""
        self.is_paused = False
        self.logger.log("密码破解已恢复")

    def stop(self):
        """停止破解"""
        self.is_running = False
        self.logger.log("密码破解已停止")

        # 清理GPU资源
        if hasattr(self, "gpu_manager"):
            self.gpu_manager.cleanup()


class PasswordCrackEngine(QObject):
    """密码破解引擎"""

    # 信号定义
    progress_updated = Signal(int, int, str)
    password_found = Signal(str, int, float)
    crack_finished = Signal(bool, str)
    speed_updated = Signal(float)

    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        self.worker = None
        self.logger = Logger()

    def start_crack(self, archive_path: str, dictionary_path: str) -> bool:
        """开始密码破解"""
        if self.worker and self.worker.isRunning():
            return False

        try:
            self.worker = PasswordCrackWorker(
                archive_path, dictionary_path, self.config
            )

            # 连接信号
            self.worker.progress_updated.connect(self.progress_updated)
            self.worker.password_found.connect(self.password_found)
            self.worker.crack_finished.connect(self.crack_finished)
            self.worker.speed_updated.connect(self.speed_updated)

            # 启动工作线程
            self.worker.start()
            return True

        except Exception as e:
            self.logger.log(f"启动密码破解失败: {str(e)}")
            return False

    def pause_crack(self):
        """暂停密码破解"""
        if self.worker and self.worker.isRunning():
            self.worker.pause()

    def resume_crack(self):
        """恢复密码破解"""
        if self.worker and self.worker.isRunning():
            self.worker.resume()

    def stop_crack(self):
        """停止密码破解"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(5000)  # 等待最多5秒

    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self.worker and self.worker.isRunning()

    def is_paused(self) -> bool:
        """检查是否暂停"""
        return self.worker and self.worker.is_paused

    def get_result(self) -> Optional[PasswordCrackResult]:
        """获取破解结果"""
        if self.worker:
            return self.worker.result
        return None
