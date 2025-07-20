"""
文件处理模块 - 处理不同格式的压缩文件
"""

import os
import zipfile
import py7zr
import rarfile
from typing import Optional, List, Union
from abc import ABC, abstractmethod


class ArchiveHandler(ABC):
    """压缩文件处理基类"""

    @abstractmethod
    def test_password(self, archive_path: str, password: str) -> bool:
        """测试密码是否正确"""
        pass

    @abstractmethod
    def extract_info(self, archive_path: str) -> dict:
        """获取压缩文件信息"""
        pass


class ZipHandler(ArchiveHandler):
    """ZIP格式处理器"""

    def test_password(self, archive_path: str, password: str) -> bool:
        """测试ZIP文件密码"""
        try:
            with zipfile.ZipFile(archive_path, "r") as zip_file:
                # 获取第一个文件进行测试
                file_list = zip_file.namelist()
                if file_list:
                    first_file = file_list[0]
                    zip_file.extract(first_file, pwd=password.encode("utf-8"))
                    return True
                return False
        except (zipfile.BadZipFile, RuntimeError, UnicodeDecodeError):
            return False
        except Exception:
            return False

    def extract_info(self, archive_path: str) -> dict:
        """获取ZIP文件信息"""
        try:
            with zipfile.ZipFile(archive_path, "r") as zip_file:
                return {
                    "file_count": len(zip_file.namelist()),
                    "has_password": any(
                        info.flag_bits & 0x1 for info in zip_file.infolist()
                    ),
                    "total_size": sum(info.file_size for info in zip_file.infolist()),
                    "compressed_size": sum(
                        info.compress_size for info in zip_file.infolist()
                    ),
                }
        except Exception as e:
            return {"error": str(e)}


class SevenZipHandler(ArchiveHandler):
    """7Z格式处理器"""

    def test_password(self, archive_path: str, password: str) -> bool:
        """测试7Z文件密码"""
        try:
            with py7zr.SevenZipFile(
                archive_path, mode="r", password=password
            ) as archive:
                # 尝试读取文件列表
                archive.list()
                return True
        except py7zr.exceptions.Bad7zFile:
            return False
        except Exception:
            return False

    def extract_info(self, archive_path: str) -> dict:
        """获取7Z文件信息"""
        try:
            with py7zr.SevenZipFile(archive_path, mode="r") as archive:
                file_list = archive.list()
                return {
                    "file_count": len(file_list),
                    "has_password": archive.needs_password(),
                    "total_size": sum(
                        item.uncompressed if item.uncompressed else 0
                        for item in file_list
                    ),
                    "compressed_size": sum(
                        item.compressed if item.compressed else 0 for item in file_list
                    ),
                }
        except Exception as e:
            return {"error": str(e)}


class RarHandler(ArchiveHandler):
    """RAR格式处理器"""

    def test_password(self, archive_path: str, password: str) -> bool:
        """测试RAR文件密码"""
        try:
            with rarfile.RarFile(archive_path, "r") as rar_file:
                rar_file.setpassword(password)
                # 获取第一个文件进行测试
                file_list = rar_file.namelist()
                if file_list:
                    first_file = file_list[0]
                    rar_file.read(first_file)
                    return True
                return False
        except (rarfile.BadRarFile, rarfile.RarWrongPassword, UnicodeDecodeError):
            return False
        except Exception:
            return False

    def extract_info(self, archive_path: str) -> dict:
        """获取RAR文件信息"""
        try:
            with rarfile.RarFile(archive_path, "r") as rar_file:
                file_list = rar_file.infolist()
                return {
                    "file_count": len(file_list),
                    "has_password": any(info.needs_password() for info in file_list),
                    "total_size": sum(info.file_size for info in file_list),
                    "compressed_size": sum(info.compress_size for info in file_list),
                }
        except Exception as e:
            return {"error": str(e)}


class ArchiveManager:
    """压缩文件管理器"""

    def __init__(self):
        self.handlers = {
            ".zip": ZipHandler(),
            ".7z": SevenZipHandler(),
            ".rar": RarHandler(),
        }
        self.supported_formats = list(self.handlers.keys())

    def get_handler(self, file_path: str) -> Optional[ArchiveHandler]:
        """根据文件扩展名获取对应的处理器"""
        ext = os.path.splitext(file_path)[1].lower()
        return self.handlers.get(ext)

    def is_supported(self, file_path: str) -> bool:
        """检查文件格式是否支持"""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.supported_formats

    def test_password(self, archive_path: str, password: str) -> bool:
        """测试压缩文件密码"""
        handler = self.get_handler(archive_path)
        if handler:
            return handler.test_password(archive_path, password)
        return False

    def get_archive_info(self, archive_path: str) -> dict:
        """获取压缩文件信息"""
        if not os.path.exists(archive_path):
            return {"error": "文件不存在"}

        handler = self.get_handler(archive_path)
        if handler:
            info = handler.extract_info(archive_path)
            info["format"] = os.path.splitext(archive_path)[1].lower()
            info["file_size"] = os.path.getsize(archive_path)
            return info
        else:
            return {"error": "不支持的文件格式"}

    def get_supported_formats_filter(self) -> str:
        """获取文件对话框的格式过滤器"""
        filters = []
        filters.append("支持的压缩文件 (*.zip *.7z *.rar)")
        filters.append("ZIP文件 (*.zip)")
        filters.append("7Z文件 (*.7z)")
        filters.append("RAR文件 (*.rar)")
        filters.append("所有文件 (*.*)")
        return ";;".join(filters)
