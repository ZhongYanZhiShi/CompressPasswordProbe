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
    SUPPORTED_FORMATS = {
        ".zip": "ZIP",
        ".7z": "7Z", 
        ".rar": "RAR"
    }
    
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
        """使用7z工具的t命令测试密码"""
        if not os.path.exists(archive_path):
            return False
            
        try:
            # 使用7z t命令测试压缩包完整性和密码
            cmd = [self.sevenzip_path, "t", f"-p{password}", archive_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            # 检查返回码和输出
            if result.returncode == 0:
                output = result.stdout.lower()
                return "everything is ok" in output
                
            return False
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, Exception) as e:
            print(f"密码测试失败: {str(e)}")
            return False
    
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
                    "note": "为避免超时，使用快速检测模式"
                }
            
            # 使用7z l命令获取详细信息
            return self._get_detailed_info(archive_path, file_size, archive_type)
            
        except Exception as e:
            return {"error": f"获取文件信息失败: {str(e)}"}
    
    def _is_volume_file(self, archive_path: str) -> bool:
        """检查是否为分卷文件"""
        filename = archive_path.lower()
        return any(
            pattern.search(filename) 
            for pattern, _ in self.VOLUME_PATTERNS.values()
        )
    
    def _get_detailed_info(self, archive_path: str, file_size: int, archive_type: str) -> Dict:
        """获取详细的压缩文件信息"""
        try:
            cmd = [self.sevenzip_path, "l", archive_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return self._parse_7z_output(result.stdout, file_size, archive_type)
            else:
                return self._get_basic_info(file_size, archive_type, "7z命令执行失败")
                
        except subprocess.TimeoutExpired:
            return self._get_basic_info(file_size, archive_type, "7z命令超时，使用基本信息")
        except Exception as e:
            return {"error": f"获取详细信息失败: {str(e)}"}
    
    def _parse_7z_output(self, output: str, file_size: int, archive_type: str) -> Dict:
        """解析7z命令输出"""
        file_count = 0
        has_password = False
        
        lines = output.split('\n')
        for line in lines:
            # 查找文件数量
            if "files" in line.lower():
                files_match = re.search(r'(\d+)\s+files?', line, re.IGNORECASE)
                if files_match:
                    file_count = int(files_match.group(1))
            
            # 检查是否有密码保护
            if any(keyword in line.lower() for keyword in ["encrypted", "aes", "method"]):
                has_password = True
        
        return {
            "file_count": file_count if file_count > 0 else 1,
            "has_password": has_password,
            "total_size": file_size,
            "compressed_size": file_size,
            "format": archive_type or "未知",
            "method": "7z工具检测"
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
            "note": note
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
            "所有文件 (*.*)"
        ]
        return ";;".join(filters)
    
    # 为了保持向后兼容，提供旧接口
    def get_handler(self, file_path: str) -> Optional[UnifiedArchiveHandler]:
        """获取处理器（向后兼容）"""
        return self.handler if self.is_supported(file_path) else None