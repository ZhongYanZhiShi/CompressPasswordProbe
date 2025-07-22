"""
字典处理模块 - 重构简化版
合并重复的读取逻辑，简化接口
"""

import os
from typing import Iterator, List, Union
from PySide6.QtCore import QObject, Signal


class DictionaryReader(QObject):
    """统一的字典文件读取器"""

    # 信号定义
    progress_updated = Signal(int, int)  # 当前进度, 总数

    def __init__(self, dictionary_path: str):
        super().__init__()
        self.dictionary_path = dictionary_path
        self.total_passwords = 0
        self.current_position = 0
        self._count_passwords()

    def _count_passwords(self) -> None:
        """计算字典文件中的密码总数"""
        try:
            with open(self.dictionary_path, "r", encoding="utf-8", errors="ignore") as f:
                self.total_passwords = sum(1 for line in f if line.strip())
        except Exception as e:
            print(f"计算密码总数失败: {e}")
            self.total_passwords = 0

    def read_passwords(self, batch_size: int = None) -> Iterator[Union[str, List[str]]]:
        """统一的密码读取方法
        
        Args:
            batch_size: 批量大小。如果为None或1，逐个返回密码；否则批量返回
        """
        try:
            with open(self.dictionary_path, "r", encoding="utf-8", errors="ignore") as f:
                if batch_size is None or batch_size <= 1:
                    # 单个读取模式
                    yield from self._read_single_passwords(f)
                else:
                    # 批量读取模式
                    yield from self._read_password_batches(f, batch_size)
        except Exception as e:
            print(f"读取字典文件失败: {e}")

    def _read_single_passwords(self, file_obj) -> Iterator[str]:
        """逐个读取密码"""
        for line_num, line in enumerate(file_obj, 1):
            password = line.strip()
            if password:
                self.current_position = line_num
                if line_num % 100 == 0:  # 每100个密码更新一次进度
                    self.progress_updated.emit(self.current_position, self.total_passwords)
                yield password

    def _read_password_batches(self, file_obj, batch_size: int) -> Iterator[List[str]]:
        """批量读取密码"""
        batch = []
        for line_num, line in enumerate(file_obj, 1):
            password = line.strip()
            if password:
                batch.append(password)
                
                if len(batch) >= batch_size:
                    self.current_position = line_num
                    self.progress_updated.emit(self.current_position, self.total_passwords)
                    yield batch
                    batch = []

        # 返回剩余的密码
        if batch:
            self.current_position = self.total_passwords
            self.progress_updated.emit(self.current_position, self.total_passwords)
            yield batch

    def get_total_passwords(self) -> int:
        """获取密码总数"""
        return self.total_passwords

    def get_current_position(self) -> int:
        """获取当前位置"""
        return self.current_position

    def validate_dictionary(self) -> dict:
        """验证字典文件"""
        result = {
            "valid": False,
            "error": None,
            "file_size": 0,
            "password_count": 0,
            "encoding": "utf-8",
        }

        try:
            if not os.path.exists(self.dictionary_path):
                result["error"] = "字典文件不存在"
                return result

            result["file_size"] = os.path.getsize(self.dictionary_path)
            
            # 简化编码检测 - 直接使用utf-8和忽略错误
            result["encoding"] = "utf-8"
            result["password_count"] = self.total_passwords
            result["valid"] = self.total_passwords > 0

        except Exception as e:
            result["error"] = str(e)

        return result
    
    # 向后兼容的方法
    def read_single_password(self) -> Iterator[str]:
        """逐个读取密码（向后兼容）"""
        return self.read_passwords(batch_size=1)


class DictionaryManager:
    """字典管理器 - 简化版"""

    # 常见密码常量
    COMMON_PASSWORDS = [
        "123456", "password", "123456789", "12345678", "12345", "1234567",
        "1234567890", "qwerty", "abc123", "111111", "123123", "admin",
        "letmein", "welcome", "monkey", "dragon", "pass", "master",
        "hello", "freedom", "whatever", "qazwsx", "trustno1", "jordan",
        "harley", "1234", "1111", "0000", "password1", "123321",
        "666666", "654321", "7777777", "123", "888888",
    ]

    @staticmethod
    def create_sample_dictionary(file_path: str, passwords: List[str] = None) -> bool:
        """创建示例字典文件"""
        if passwords is None:
            passwords = DictionaryManager.COMMON_PASSWORDS
            
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                for password in passwords:
                    f.write(f"{password}\n")
            return True
        except Exception as e:
            print(f"创建示例字典失败: {e}")
            return False

    @staticmethod  
    def get_common_passwords() -> List[str]:
        """获取常见密码列表"""
        return DictionaryManager.COMMON_PASSWORDS.copy()

    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """验证文件路径"""
        return os.path.exists(file_path) and os.path.isfile(file_path)