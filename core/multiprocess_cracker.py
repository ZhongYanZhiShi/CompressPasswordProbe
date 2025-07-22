"""
多进程密码破解引擎
支持并行密码验证，显著提升破解速度
"""

import os
import time
import multiprocessing as mp
from typing import Optional, List, Tuple, Dict, Any
from queue import Empty
from PySide6.QtCore import QObject, Signal, QThread

from .archive_handler import ArchiveManager
from .dictionary import DictionaryReader
from .logger import Logger


def worker_process_test_password(
    args: Tuple[str, str, str, int, Optional[Dict]],
) -> Tuple[bool, str, int, float]:
    """
    工作进程函数 - 测试单个密码 (优化版本)

    Args:
        args: (archive_path, password, sevenzip_path, worker_id, smallest_file_info)

    Returns:
        (success, password, worker_id, test_time)
    """
    archive_path, password, sevenzip_path, worker_id, smallest_file_info = args
    start_time = time.time()

    try:
        # 在子进程中创建独立的ArchiveManager，但避免重复文件分析
        os.environ["SEVENZIP_PATH"] = sevenzip_path
        archive_manager = ArchiveManager()

        # 如果传入了预分析的最小文件信息，直接使用优化的测试方法
        if smallest_file_info:
            success = archive_manager.handler._test_password_with_preanalyzed_file(
                archive_path, password, smallest_file_info
            )
        else:
            success = archive_manager.test_password(archive_path, password)

        test_time = time.time() - start_time
        return (success, password, worker_id, test_time)

    except Exception as e:
        test_time = time.time() - start_time
        if worker_id == 0:  # 只让第一个进程输出错误，避免重复
            print(f"工作进程{worker_id}测试密码'{password}'时出错: {str(e)}")
        return (False, password, worker_id, test_time)


def worker_process_batch_test(
    args: Tuple[str, List[str], str, int, Optional[Dict]],
) -> Tuple[Optional[str], int, List[float]]:
    """
    工作进程函数 - 批量测试密码 (优化版本)

    Args:
        args: (archive_path, password_batch, sevenzip_path, batch_id, smallest_file_info)

    Returns:
        (found_password, batch_id, test_times)
    """
    archive_path, password_batch, sevenzip_path, batch_id, smallest_file_info = args
    test_times = []

    try:
        # 获取当前进程的真实ID
        import multiprocessing

        actual_process_id = multiprocessing.current_process().pid
        process_name = multiprocessing.current_process().name

        # 在子进程中创建独立的ArchiveManager - 避免重复日志输出
        os.environ["SEVENZIP_PATH"] = sevenzip_path
        archive_manager = ArchiveManager()

        # 只在第一个批次时输出进程信息
        if batch_id == 0:
            print(f"进程池工作: {process_name} (PID: {actual_process_id})")

        if password_batch:
            print(
                f"批次{batch_id} [{process_name}]: 开始测试{len(password_batch)}个密码"
            )

        for i, password in enumerate(password_batch):
            start_time = time.time()

            # 使用预分析信息进行优化测试
            if smallest_file_info:
                success = archive_manager.handler._test_password_with_preanalyzed_file(
                    archive_path, password, smallest_file_info
                )
            else:
                success = archive_manager.test_password(archive_path, password)

            test_time = time.time() - start_time
            test_times.append(test_time)

            if success:
                print(
                    f"批次{batch_id} [{process_name}]: 找到正确密码 '{password}' (第{i+1}/{len(password_batch)}个)"
                )
                return (password, batch_id, test_times)

            # 每测试20个密码输出一次进度，减少日志频率
            if (i + 1) % 20 == 0:
                avg_time = sum(test_times[-20:]) / 20
                print(
                    f"批次{batch_id} [{process_name}]: 已测试 {i+1}/{len(password_batch)} 个密码 (平均 {avg_time:.2f}s/密码)"
                )

        print(f"批次{batch_id} [{process_name}]: 批次完成，未找到正确密码")
        return (None, batch_id, test_times)

    except Exception as e:
        print(f"批次{batch_id}: 批量测试时出错: {str(e)}")
        return (None, batch_id, test_times)


class MultiprocessPasswordCracker(QThread):
    """多进程密码破解器"""

    # Qt信号
    progress_updated = Signal(int, int, str, float)  # 当前进度, 总数, 当前密码, 速度
    password_found = Signal(str, int, float)  # 找到的密码, 尝试次数, 耗时
    crack_finished = Signal(bool, str, dict)  # 是否成功, 错误信息, 统计信息

    def __init__(self, archive_path: str, dictionary_path: str, config: Dict[str, Any]):
        super().__init__()

        self.archive_path = archive_path
        self.dictionary_path = dictionary_path
        self.config = config
        self.logger = Logger()

        # 优化并发配置
        cpu_count = mp.cpu_count()
        default_processes = min(8, cpu_count)  # 限制最大进程数为8或CPU核数
        self.max_processes = min(
            config.get("max_processes", default_processes), 16
        )  # 硬限制16个进程
        self.batch_size = config.get("batch_size", 100)  # 减少批次大小，提高响应性
        self.max_attempts = config.get("max_attempts", 0)  # 0表示无限制

        # 运行状态
        self.is_running = False
        self.is_paused = False
        self.found_password = None

        # 统计信息
        self.total_attempts = 0
        self.start_time = 0
        self.process_pool = None

        # 预分析压缩包信息，避免每个进程重复分析
        self.smallest_file_info = None

        # 获取7z工具路径
        archive_manager = ArchiveManager()
        self.sevenzip_path = archive_manager.handler.sevenzip_path

        print(
            f"多进程破解器初始化: {self.max_processes}进程 (CPU核数: {cpu_count}), 批次大小{self.batch_size}"
        )
        self._preanalyze_archive()

    def _preanalyze_archive(self):
        """预分析压缩包，获取最小文件信息，避免每个进程重复分析"""
        try:
            print("预分析压缩包，优化多进程性能...")
            archive_manager = ArchiveManager()

            # 获取最小的加密文件信息
            self.smallest_file_info = (
                archive_manager.handler._find_smallest_encrypted_file(self.archive_path)
            )

            if self.smallest_file_info:
                print(
                    f"预分析完成: 找到测试文件 {self.smallest_file_info['name']} ({self.smallest_file_info.get('size', 0)} bytes)"
                )
            else:
                print("预分析: 将使用完整压缩包测试模式")

        except Exception as e:
            print(f"预分析失败，将使用标准测试模式: {str(e)}")
            self.smallest_file_info = None

    def start_cracking(self):
        """开始密码破解"""
        self.is_running = True
        self.is_paused = False
        self.found_password = None
        self.total_attempts = 0
        self.start_time = time.time()

        self.start()

    def pause_cracking(self):
        """暂停破解"""
        self.is_paused = True
        print("破解已暂停")

    def resume_cracking(self):
        """恢复破解"""
        self.is_paused = False
        print("破解已恢复")

    def stop_cracking(self):
        """停止破解"""
        self.is_running = False
        if self.process_pool:
            self.process_pool.terminate()
            self.process_pool.join()
            self.process_pool = None
        print("破解已停止")

    def run(self):
        """主破解逻辑"""
        try:
            # 初始化破解状态
            if self.start_time == 0:
                self.start_time = time.time()
            self.is_running = True
            self.found_password = None
            self.total_attempts = 0

            # 检查压缩包
            if not os.path.exists(self.archive_path):
                self.crack_finished.emit(False, "压缩包文件不存在", {})
                return

            # 检查字典文件
            if not os.path.exists(self.dictionary_path):
                self.crack_finished.emit(False, "字典文件不存在", {})
                return

            print(f"开始多进程密码破解: {self.archive_path}")
            print(f"字典文件: {self.dictionary_path}")
            print(f"优化配置: {self.max_processes}进程, 批次大小: {self.batch_size}")
            print("=" * 60)

            # 创建进程池
            self.process_pool = mp.Pool(processes=self.max_processes)
            print(f"已创建进程池: {self.max_processes} 个工作进程")
            print(f"进程池类型: {type(self.process_pool)}")

            # 读取字典并分批处理
            dictionary_reader = DictionaryReader(self.dictionary_path)

            batch_count = 0
            current_batch = []
            pending_results = []

            # 控制并发任务数量，避免创建过多批次
            max_concurrent_batches = (
                self.max_processes * 2
            )  # 最多允许进程数的2倍批次并发
            print(f"最大并发批次: {max_concurrent_batches}")

            # 获取密码生成器
            password_generator = dictionary_reader.read_single_password()

            while self.is_running and not self.found_password:
                # 处理暂停
                while self.is_paused and self.is_running:
                    time.sleep(0.1)

                if not self.is_running:
                    break

                # 读取密码构建批次
                if len(current_batch) < self.batch_size:
                    try:
                        password = next(password_generator)
                        current_batch.append(password)
                        continue
                    except StopIteration:
                        # 字典已读完
                        print(
                            f"字典读取完毕，当前批次: {len(current_batch)}, 等待批次: {len(pending_results)}"
                        )
                        if not current_batch and not pending_results:
                            break

                # 提交批次任务 (控制并发数量)
                if current_batch and len(pending_results) < max_concurrent_batches:
                    batch_args = (
                        self.archive_path,
                        current_batch.copy(),
                        self.sevenzip_path,
                        batch_count,
                        self.smallest_file_info,  # 传入预分析的文件信息
                    )

                    result = self.process_pool.apply_async(
                        worker_process_batch_test, (batch_args,)
                    )
                    pending_results.append((result, len(current_batch), batch_count))

                    # 输出批次提交信息
                    if batch_count < 5:  # 只显示前5个批次的信息
                        print(f"提交批次 {batch_count}: {len(current_batch)} 个密码")

                    batch_count += 1
                    current_batch.clear()

                # 检查已完成的任务
                completed_results = []
                for result, batch_size, batch_id in pending_results:
                    if result.ready():
                        completed_results.append((result, batch_size, batch_id))

                # 处理完成的结果
                for result, batch_size, batch_id in completed_results:
                    pending_results = [
                        (r, s, i) for r, s, i in pending_results if i != batch_id
                    ]

                    try:
                        found_password, returned_batch_id, test_times = result.get(
                            timeout=1
                        )

                        self.total_attempts += batch_size

                        # 计算速度
                        elapsed_time = time.time() - self.start_time
                        speed = (
                            self.total_attempts / elapsed_time
                            if elapsed_time > 0
                            else 0
                        )

                        # 更好的进度反馈
                        if (
                            self.total_attempts % (self.batch_size * 2) == 0
                            or found_password
                        ):
                            progress_msg = f"进度: 已测试 {self.total_attempts} 个密码, 速度: {speed:.1f} 密码/秒"
                            if (
                                batch_id % 4 == 0 or found_password
                            ):  # 减少输出频率，但找到密码时总是输出
                                print(progress_msg)

                        # 更新进度信号
                        last_password = (
                            current_batch[-1] if current_batch else f"批次-{batch_id}"
                        )
                        self.progress_updated.emit(
                            self.total_attempts,
                            (
                                self.max_attempts
                                if self.max_attempts > 0
                                else self.total_attempts
                            ),
                            last_password,
                            speed,
                        )

                        # 检查是否找到密码
                        if found_password:
                            print(f"🎉 找到密码: '{found_password}' (批次{batch_id})")
                            self.found_password = found_password

                            self.password_found.emit(
                                found_password, self.total_attempts, elapsed_time
                            )

                            # 统计信息
                            stats = {
                                "total_attempts": self.total_attempts,
                                "elapsed_time": elapsed_time,
                                "average_speed": speed,
                                "processes_used": self.max_processes,
                                "batch_size": self.batch_size,
                                "efficiency": (
                                    f"{self.total_attempts / (self.max_processes * elapsed_time):.1f}"
                                    if elapsed_time > 0
                                    else "0"
                                ),
                            }

                            self.crack_finished.emit(
                                True, f"密码破解成功: {found_password}", stats
                            )
                            return

                        # 检查是否达到最大尝试次数
                        if (
                            self.max_attempts > 0
                            and self.total_attempts >= self.max_attempts
                        ):
                            print(f"达到最大尝试次数限制: {self.max_attempts}")
                            break

                    except Exception as e:
                        print(f"处理批次{batch_id}结果时出错: {str(e)}")

                # 避免CPU占用过高
                time.sleep(0.01)

            # 等待剩余任务完成
            if pending_results:
                print(f"等待{len(pending_results)}个批次完成...")
                for result, batch_size, batch_id in pending_results:
                    try:
                        found_password, returned_batch_id, test_times = result.get(
                            timeout=30
                        )
                        self.total_attempts += batch_size

                        if found_password and not self.found_password:
                            self.found_password = found_password
                            elapsed_time = time.time() - self.start_time
                            self.password_found.emit(
                                found_password, self.total_attempts, elapsed_time
                            )

                            stats = {
                                "total_attempts": self.total_attempts,
                                "elapsed_time": elapsed_time,
                                "average_speed": self.total_attempts / elapsed_time,
                                "processes_used": self.max_processes,
                                "batch_size": self.batch_size,
                                "efficiency": (
                                    f"{self.total_attempts / (self.max_processes * elapsed_time):.1f}"
                                    if elapsed_time > 0
                                    else "0"
                                ),
                            }

                            self.crack_finished.emit(
                                True, f"密码破解成功: {found_password}", stats
                            )
                            return

                    except Exception as e:
                        print(f"等待批次{batch_id}完成时出错: {str(e)}")

            # 破解结束
            elapsed_time = time.time() - self.start_time

            if self.found_password:
                return  # 已经在上面处理了成功情况

            # 未找到密码
            stats = {
                "total_attempts": self.total_attempts,
                "elapsed_time": elapsed_time,
                "average_speed": (
                    self.total_attempts / elapsed_time if elapsed_time > 0 else 0
                ),
                "processes_used": self.max_processes,
                "batch_size": self.batch_size,
                "efficiency": (
                    f"{self.total_attempts / (self.max_processes * elapsed_time):.1f}"
                    if elapsed_time > 0
                    else "0"
                ),
            }

            if self.total_attempts == 0:
                self.crack_finished.emit(False, "字典文件为空或无法读取", stats)
            else:
                self.crack_finished.emit(
                    False, f"密码破解失败，已尝试{self.total_attempts}个密码", stats
                )

        except Exception as e:
            error_msg = f"密码破解过程出错: {str(e)}"
            print(error_msg)
            self.crack_finished.emit(False, error_msg, {})

        finally:
            # 清理进程池
            if self.process_pool:
                self.process_pool.terminate()
                self.process_pool.join()
                self.process_pool = None
            self.is_running = False
