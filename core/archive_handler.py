"""
文件处理模块 - 处理不同格式的压缩文件
"""

import os
import re
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

        # 分卷压缩包模式
        self.volume_patterns = {
            # ZIP分卷模式：.z01, .z02, ..., .z99
            "zip_volume": re.compile(r"\.z\d{2}$", re.IGNORECASE),
            # RAR分卷模式1：.r00, .r01, ..., .r99
            "rar_volume1": re.compile(r"\.r\d{2}$", re.IGNORECASE),
            # RAR分卷模式2：.part1.rar, .part2.rar, ...
            "rar_volume2": re.compile(r"\.part\d+\.rar$", re.IGNORECASE),
            # 7Z分卷模式：.7z.001, .7z.002, ...
            "7z_volume": re.compile(r"\.7z\.\d{3}$", re.IGNORECASE),
        }

    def _detect_archive_type(self, file_path: str) -> Optional[str]:
        """检测压缩文件类型，支持分卷压缩包"""
        filename = os.path.basename(file_path).lower()
        ext = os.path.splitext(file_path)[1].lower()

        # 首先检查标准格式
        if ext in self.supported_formats:
            return ext

        # 检查分卷格式
        for pattern_name, pattern in self.volume_patterns.items():
            if pattern.search(filename):
                if pattern_name.startswith("zip"):
                    return ".zip"
                elif pattern_name.startswith("rar"):
                    return ".rar"
                elif pattern_name.startswith("7z"):
                    return ".7z"

        return None

    def get_handler(self, file_path: str) -> Optional[ArchiveHandler]:
        """根据文件扩展名获取对应的处理器"""
        archive_type = self._detect_archive_type(file_path)
        return self.handlers.get(archive_type) if archive_type else None

    def is_supported(self, file_path: str) -> bool:
        """检查文件格式是否支持"""
        return self._detect_archive_type(file_path) is not None

    def _find_first_volume(self, file_path: str) -> str:
        """查找分卷压缩包的第一卷"""
        filename = os.path.basename(file_path)
        dirname = os.path.dirname(file_path)

        # 对于分卷压缩包，尝试找到第一卷
        base_name = filename.lower()

        # ZIP分卷：找 .zip 文件
        if re.search(r"\.z\d{2}$", base_name):
            zip_name = re.sub(r"\.z\d{2}$", ".zip", base_name)
            zip_path = os.path.join(dirname, zip_name)
            if os.path.exists(zip_path):
                return zip_path

        # RAR分卷模式1：找 .rar 文件
        elif re.search(r"\.r\d{2}$", base_name):
            rar_name = re.sub(r"\.r\d{2}$", ".rar", base_name)
            rar_path = os.path.join(dirname, rar_name)
            if os.path.exists(rar_path):
                return rar_path

        # RAR分卷模式2：找 .part1.rar 文件
        elif re.search(r"\.part\d+\.rar$", base_name):
            part1_name = re.sub(r"\.part\d+\.rar$", ".part1.rar", base_name)
            part1_path = os.path.join(dirname, part1_name)
            if os.path.exists(part1_path):
                return part1_path

        # 7Z分卷：找 .7z.001 文件
        elif re.search(r"\.7z\.\d{3}$", base_name):
            first_name = re.sub(r"\.7z\.\d{3}$", ".7z.001", base_name)
            first_path = os.path.join(dirname, first_name)
            if os.path.exists(first_path):
                return first_path

        # 如果找不到第一卷，返回原文件路径
        return file_path

    def test_password(self, archive_path: str, password: str) -> bool:
        """测试压缩文件密码"""
        # 对于分卷压缩包，使用第一卷进行测试
        first_volume_path = self._find_first_volume(archive_path)
        handler = self.get_handler(first_volume_path)
        if handler:
            return handler.test_password(first_volume_path, password)
        return False

    def get_archive_info(self, archive_path: str) -> dict:
        """获取压缩文件信息"""
        if not os.path.exists(archive_path):
            return {"error": "文件不存在"}

        # 对于分卷压缩包，使用第一卷获取信息
        first_volume_path = self._find_first_volume(archive_path)
        handler = self.get_handler(first_volume_path)
        if handler:
            info = handler.extract_info(first_volume_path)
            archive_type = self._detect_archive_type(archive_path)
            info["format"] = archive_type if archive_type else "未知"
            info["file_size"] = os.path.getsize(archive_path)

            # 如果是分卷压缩包，添加分卷信息
            if first_volume_path != archive_path:
                info["is_volume"] = True
                info["first_volume"] = first_volume_path
                info["current_volume"] = archive_path
            else:
                info["is_volume"] = False

            return info
        else:
            return {"error": "不支持的文件格式"}

    def get_supported_formats_filter(self) -> str:
        """获取文件对话框的格式过滤器"""
        filters = []
        filters.append("支持的压缩文件 (*.zip *.7z *.rar *.z* *.r* *.part*.rar *.7z.*)")
        filters.append("ZIP文件 (*.zip *.z*)")
        filters.append("7Z文件 (*.7z *.7z.*)")
        filters.append("RAR文件 (*.rar *.r* *.part*.rar)")
        filters.append("所有文件 (*.*)")
        return ";;".join(filters)
