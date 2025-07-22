"""
文件处理模块 - 处理不同格式的压缩文件
重构版本：统一使用7z工具处理所有格式
"""

import os
import re
import subprocess
from typing import Optional, Dict, List


class ArchiveError(Exception):
    """压缩文件处理异常"""

    pass


class UnifiedArchiveHandler:
    """统一的压缩文件处理器 - 基于7z工具"""

    # 支持的格式和对应的文件扩展名
    SUPPORTED_FORMATS = {".zip": "ZIP", ".7z": "7Z", ".rar": "RAR"}

    # 大文件阈值（字节）- 超过此大小使用单文件解压优化
    LARGE_FILE_THRESHOLD = 100 * 1024 * 1024  # 100MB

    # 分卷压缩包模式
    VOLUME_PATTERNS = {
        # ZIP分卷模式：.z01, .z02, ..., .z99
        "zip_volume": (re.compile(r"\.z\d{2}$", re.IGNORECASE), ".zip"),
        # RAR分卷模式1：.r00, .r01, ..., .r99
        "rar_volume1": (re.compile(r"\.r\d{2}$", re.IGNORECASE), ".rar"),
        # RAR分卷模式2：.part1.rar, .part2.rar, ...
        "rar_volume2": (re.compile(r"\.part\d+\.rar$", re.IGNORECASE), ".rar"),
        # 7Z分卷模式：.7z.001, .7z.002, ...
        "7z_volume": (re.compile(r"\.7z\.\d{3}$", re.IGNORECASE), ".7z"),
    }

    def __init__(self):
        self.sevenzip_path = self._find_bundled_7zip()
        if not self.sevenzip_path:
            raise ArchiveError("7z工具不可用，无法处理压缩文件")
        print(f"7z工具路径: {self.sevenzip_path}")

    def _find_bundled_7zip(self) -> Optional[str]:
        """查找项目打包的7z工具"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        bundled_7z_path = os.path.join(current_dir, "..", "lib", "7z", "win", "7z.exe")
        bundled_7z_path = os.path.abspath(bundled_7z_path)

        if os.path.exists(bundled_7z_path):
            return bundled_7z_path
        return None

    def detect_archive_type(self, file_path: str) -> Optional[str]:
        """检测压缩文件类型，支持分卷压缩包"""
        filename = os.path.basename(file_path).lower()
        ext = os.path.splitext(file_path)[1].lower()

        # 首先检查标准格式
        if ext in self.SUPPORTED_FORMATS:
            return ext

        # 检查分卷格式
        for pattern_name, (pattern, format_ext) in self.VOLUME_PATTERNS.items():
            if pattern.search(filename):
                return format_ext

        return None

    def is_supported(self, file_path: str) -> bool:
        """检查文件格式是否支持"""
        return self.detect_archive_type(file_path) is not None

    def find_first_volume(self, file_path: str) -> str:
        """查找分卷压缩包的第一卷"""
        filename = os.path.basename(file_path)
        dirname = os.path.dirname(file_path)
        base_name = filename.lower()

        # 分卷文件名映射规则
        volume_rules = [
            # ZIP分卷：找 .zip 文件
            (r"\.z\d{2}$", ".zip"),
            # RAR分卷模式1：找 .rar 文件
            (r"\.r\d{2}$", ".rar"),
            # RAR分卷模式2：找 .part1.rar 文件
            (r"\.part\d+\.rar$", ".part1.rar"),
            # 7Z分卷：找 .7z.001 文件
            (r"\.7z\.\d{3}$", ".7z.001"),
        ]

        for pattern, replacement in volume_rules:
            if re.search(pattern, base_name):
                first_name = re.sub(pattern, replacement, base_name)
                first_path = os.path.join(dirname, first_name)
                if os.path.exists(first_path):
                    return first_path

        # 如果找不到第一卷，返回原文件路径
        return file_path

    def test_password(self, archive_path: str, password: str) -> bool:
        """使用7z工具测试密码 - 支持大文件优化"""
        if not os.path.exists(archive_path):
            return False

        # 检查文件大小，决定使用哪种测试方法
        file_size = os.path.getsize(archive_path)
        if file_size > self.LARGE_FILE_THRESHOLD:
            print(
                f"检测到大文件 ({file_size / (1024*1024):.1f}MB)，使用单文件解压优化..."
            )
            return self._test_password_with_single_file_extraction(
                archive_path, password
            )
        else:
            return self._test_password_with_full_test(archive_path, password)

    def _test_password_with_full_test(self, archive_path: str, password: str) -> bool:
        """使用7z t命令测试整个压缩包（适用于小文件）"""
        try:
            # 使用7z t命令测试压缩包完整性和密码
            cmd = [self.sevenzip_path, "t", f"-p{password}", archive_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            # 检查返回码和输出
            if result.returncode == 0:
                output = result.stdout.lower()
                return "everything is ok" in output

            return False

        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
            Exception,
        ) as e:
            print(f"密码测试失败: {str(e)}")
            return False

    def _test_password_with_single_file_extraction(
        self, archive_path: str, password: str
    ) -> bool:
        """通过单文件解压测试密码（适用于大文件优化）"""
        try:
            # 获取最小的加密文件
            smallest_file = self._find_smallest_encrypted_file(archive_path)
            if not smallest_file:
                print("未找到合适的测试文件，回退到完整测试...")
                return self._test_password_with_full_test(archive_path, password)

            print(
                f"使用最小文件进行测试: {smallest_file['name']} ({smallest_file['size']} bytes)"
            )

            # 使用7z e命令解压单个文件到临时位置
            import tempfile

            temp_dir = tempfile.mkdtemp()

            try:
                # 修复文件名路径分隔符 - 7z需要单反斜杠才能正确匹配Unicode文件名
                target_filename = smallest_file["name"].replace("\\\\", "\\")

                cmd = [
                    self.sevenzip_path,
                    "e",
                    f"-p{password}",
                    archive_path,
                    target_filename,
                    f"-o{temp_dir}",  # 输出到临时目录
                    "-y",  # 自动回答yes
                ]

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

                # 检查结果 - 更严格的检查逻辑
                error_output = result.stderr
                stdout_output = result.stdout

                if result.returncode == 0:
                    # 检查是否真的解压了文件
                    if (
                        "Files: 0" in stdout_output
                        or "No files to process" in stdout_output
                    ):
                        print("文件名匹配失败，回退到完整测试")
                        return self._test_password_with_full_test(
                            archive_path, password
                        )
                    else:
                        # 真正成功解压，密码正确
                        return True
                else:
                    # 检查是否是密码错误
                    if (
                        "wrong password" in error_output.lower()
                        or "wrong password" in stdout_output.lower()
                        or "ERROR:" in error_output
                        and "password" in error_output.lower()
                    ):
                        return False
                    else:
                        # 其他错误，可能需要回退
                        print(f"单文件解压遇到未知错误，回退到完整测试")
                        return self._test_password_with_full_test(
                            archive_path, password
                        )

            finally:
                # 清理临时目录
                import shutil

                shutil.rmtree(temp_dir, ignore_errors=True)

        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
            Exception,
        ) as e:
            print(f"单文件解压测试失败，回退到完整测试: {str(e)}")
            return self._test_password_with_full_test(archive_path, password)

    def _find_smallest_encrypted_file(self, archive_path: str) -> Optional[Dict]:
        """查找压缩包中最小的文件作为密码测试目标"""
        try:
            # 使用7z l命令获取详细文件列表
            cmd = [self.sevenzip_path, "l", "-slt", archive_path]  # -slt: 技术信息模式
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                return None

            return self._parse_file_list_for_smallest(result.stdout)

        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
            Exception,
        ) as e:
            print(f"获取文件列表失败: {str(e)}")
            return None

    def _parse_file_list_for_smallest(self, list_output: str) -> Optional[Dict]:
        """解析7z列表输出，找到最小的非目录文件"""
        files = []
        current_file = {}

        lines = list_output.split("\n")
        for line in lines:
            line = line.strip()

            if line.startswith("Path = "):
                # 保存上一个文件（如果有的话）
                if current_file and self._is_valid_test_file(current_file):
                    files.append(current_file.copy())

                # 开始新文件
                current_file = {"name": line[7:]}  # 移除 "Path = "

            elif line.startswith("Size = "):
                try:
                    current_file["size"] = int(line[7:])
                except ValueError:
                    current_file["size"] = 0

            elif line.startswith("Attributes = "):
                current_file["attributes"] = line[13:]

            elif line.startswith("Encrypted = "):
                current_file["encrypted"] = line[12:].strip() == "+"

        # 处理最后一个文件
        if current_file and self._is_valid_test_file(current_file):
            files.append(current_file)

        if not files:
            return None

        # 优先选择目录层级浅且文件小的 - 避免Unicode路径匹配问题
        def get_file_priority(f):
            name = f.get("name", "")
            size = f.get("size", float("inf"))
            # 计算目录层级深度（反斜杠数量）
            depth = name.count("\\") + name.count("/")
            # 优先级：目录深度权重更高，然后是文件大小
            return (depth, size)

        files.sort(key=get_file_priority)
        best_file = files[0]

        depth = best_file.get("name", "").count("\\") + best_file.get("name", "").count(
            "/"
        )
        print(
            f"找到 {len(files)} 个候选文件，选择层级最浅的: {best_file['name']} (深度:{depth}, 大小:{best_file.get('size', 0)} bytes)"
        )
        return best_file

    def _is_valid_test_file(self, file_info: Dict) -> bool:
        """判断文件是否适合用于密码测试"""
        # 检查基本信息
        if not file_info.get("name"):
            return False

        name = file_info["name"]
        size = file_info.get("size", 0)
        attributes = file_info.get("attributes", "")

        # 排除目录
        if "D" in attributes or name.endswith("/") or name.endswith("\\"):
            return False

        # 排除过大的文件（超过10MB的单个文件）
        if size > 10 * 1024 * 1024:
            return False

        # 排除0字节文件
        if size <= 0:
            return False

        # 优先选择常见的小文件类型
        name_lower = name.lower()
        preferred_extensions = [
            ".txt",
            ".jpg",
            ".png",
            ".gif",
            ".pdf",
            ".doc",
            ".xml",
            ".json",
            ".ini",
        ]

        # 如果是首选类型，给予额外权重（通过调整size实现）
        if any(name_lower.endswith(ext) for ext in preferred_extensions):
            file_info["priority"] = True
        else:
            file_info["priority"] = False

        return True

    def extract_info(self, archive_path: str) -> Dict:
        """获取压缩文件信息"""
        if not os.path.exists(archive_path):
            return {"error": "文件不存在"}

        try:
            file_size = os.path.getsize(archive_path)
            archive_type = self.detect_archive_type(archive_path)

            # 对于分卷文件，提供基本信息避免超时
            if self._is_volume_file(archive_path):
                return {
                    "file_count": 1,
                    "has_password": True,
                    "total_size": file_size,
                    "compressed_size": file_size,
                    "format": archive_type or "未知",
                    "method": "快速模式 - 分卷文件",
                    "note": "为避免超时，使用快速检测模式",
                }

            # 使用7z l命令获取详细信息
            return self._get_detailed_info(archive_path, file_size, archive_type)

        except Exception as e:
            return {"error": f"获取文件信息失败: {str(e)}"}

    def _is_volume_file(self, archive_path: str) -> bool:
        """检查是否为分卷文件"""
        filename = archive_path.lower()
        return any(
            pattern.search(filename) for pattern, _ in self.VOLUME_PATTERNS.values()
        )

    def _get_detailed_info(
        self, archive_path: str, file_size: int, archive_type: str
    ) -> Dict:
        """获取详细的压缩文件信息"""
        try:
            cmd = [self.sevenzip_path, "l", archive_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                return self._parse_7z_output(result.stdout, file_size, archive_type)
            else:
                return self._get_basic_info(file_size, archive_type, "7z命令执行失败")

        except subprocess.TimeoutExpired:
            return self._get_basic_info(
                file_size, archive_type, "7z命令超时，使用基本信息"
            )
        except Exception as e:
            return {"error": f"获取详细信息失败: {str(e)}"}

    def _parse_7z_output(self, output: str, file_size: int, archive_type: str) -> Dict:
        """解析7z命令输出"""
        file_count = 0
        has_password = False

        lines = output.split("\n")
        for line in lines:
            # 查找文件数量
            if "files" in line.lower():
                files_match = re.search(r"(\d+)\s+files?", line, re.IGNORECASE)
                if files_match:
                    file_count = int(files_match.group(1))

            # 检查是否有密码保护
            if any(
                keyword in line.lower() for keyword in ["encrypted", "aes", "method"]
            ):
                has_password = True

        return {
            "file_count": file_count if file_count > 0 else 1,
            "has_password": has_password,
            "total_size": file_size,
            "compressed_size": file_size,
            "format": archive_type or "未知",
            "method": "7z工具检测",
        }

    def _get_basic_info(self, file_size: int, archive_type: str, note: str) -> Dict:
        """获取基本文件信息"""
        return {
            "file_count": 1,
            "has_password": True,
            "total_size": file_size,
            "compressed_size": file_size,
            "format": archive_type or "未知",
            "method": "快速模式",
            "note": note,
        }


class ArchiveManager:
    """压缩文件管理器 - 简化版"""

    def __init__(self):
        self.handler = UnifiedArchiveHandler()

    @property
    def supported_formats(self) -> List[str]:
        """支持的格式列表"""
        return list(self.handler.SUPPORTED_FORMATS.keys())

    def is_supported(self, file_path: str) -> bool:
        """检查文件格式是否支持"""
        return self.handler.is_supported(file_path)

    def test_password(self, archive_path: str, password: str) -> bool:
        """测试压缩文件密码"""
        # 对于分卷压缩包，使用第一卷进行测试
        first_volume_path = self.handler.find_first_volume(archive_path)
        return self.handler.test_password(first_volume_path, password)

    def get_archive_info(self, archive_path: str) -> Dict:
        """获取压缩文件信息"""
        # 对于分卷压缩包，使用第一卷获取信息
        first_volume_path = self.handler.find_first_volume(archive_path)
        info = self.handler.extract_info(first_volume_path)

        # 添加分卷信息
        if first_volume_path != archive_path:
            info["is_volume"] = True
            info["first_volume"] = first_volume_path
            info["current_volume"] = archive_path
        else:
            info["is_volume"] = False

        # 添加当前文件的大小信息
        if os.path.exists(archive_path):
            info["file_size"] = os.path.getsize(archive_path)

        return info

    def get_supported_formats_filter(self) -> str:
        """获取文件对话框的格式过滤器"""
        filters = [
            "支持的压缩文件 (*.zip *.7z *.rar *.z* *.r* *.part*.rar *.7z.*)",
            "ZIP文件 (*.zip *.z*)",
            "7Z文件 (*.7z *.7z.*)",
            "RAR文件 (*.rar *.r* *.part*.rar)",
            "所有文件 (*.*)",
        ]
        return ";;".join(filters)

    # 为了保持向后兼容，提供旧接口
    def get_handler(self, file_path: str) -> Optional[UnifiedArchiveHandler]:
        """获取处理器（向后兼容）"""
        return self.handler if self.is_supported(file_path) else None
