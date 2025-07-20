"""
GPU加速模块
"""

import os
import platform
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod

# GPU相关库的导入（可选）
try:
    import pycuda.driver as cuda
    import pycuda.autoinit
    from pycuda.compiler import SourceModule

    CUDA_AVAILABLE = True
except ImportError:
    CUDA_AVAILABLE = False

try:
    import pyopencl as cl

    OPENCL_AVAILABLE = True
except ImportError:
    OPENCL_AVAILABLE = False

try:
    from numba import cuda as numba_cuda

    NUMBA_CUDA_AVAILABLE = True
except ImportError:
    NUMBA_CUDA_AVAILABLE = False


class GPUAccelerator(ABC):
    """GPU加速器基类"""

    @abstractmethod
    def is_available(self) -> bool:
        """检查GPU是否可用"""
        pass

    @abstractmethod
    def get_device_info(self) -> Dict[str, Any]:
        """获取设备信息"""
        pass

    @abstractmethod
    def test_passwords_batch(self, passwords: List[str], test_func) -> Optional[str]:
        """批量测试密码"""
        pass


class CUDAAccelerator(GPUAccelerator):
    """CUDA加速器"""

    def __init__(self):
        self.context = None
        self.device = None

    def is_available(self) -> bool:
        """检查CUDA是否可用"""
        if not CUDA_AVAILABLE:
            return False

        try:
            cuda.init()
            self.device = cuda.Device(0)
            self.context = self.device.make_context()
            return True
        except Exception:
            return False

    def get_device_info(self) -> Dict[str, Any]:
        """获取CUDA设备信息"""
        if not self.is_available():
            return {}

        try:
            return {
                "name": self.device.name(),
                "compute_capability": self.device.compute_capability(),
                "total_memory": self.device.total_memory(),
                "multiprocessor_count": self.device.get_attribute(
                    cuda.device_attribute.MULTIPROCESSOR_COUNT
                ),
                "max_threads_per_block": self.device.get_attribute(
                    cuda.device_attribute.MAX_THREADS_PER_BLOCK
                ),
                "type": "CUDA",
            }
        except Exception:
            return {}

    def test_passwords_batch(self, passwords: List[str], test_func) -> Optional[str]:
        """使用CUDA批量测试密码"""
        # 由于压缩文件解密通常涉及复杂的算法，
        # 这里提供一个框架，实际实现需要根据具体的解密算法来定制
        # 目前回退到CPU并行处理
        return None

    def cleanup(self):
        """清理资源"""
        if self.context:
            self.context.pop()


class OpenCLAccelerator(GPUAccelerator):
    """OpenCL加速器"""

    def __init__(self):
        self.context = None
        self.device = None
        self.queue = None

    def is_available(self) -> bool:
        """检查OpenCL是否可用"""
        if not OPENCL_AVAILABLE:
            return False

        try:
            platforms = cl.get_platforms()
            if not platforms:
                return False

            devices = platforms[0].get_devices(cl.device_type.GPU)
            if not devices:
                return False

            self.device = devices[0]
            self.context = cl.Context([self.device])
            self.queue = cl.CommandQueue(self.context)
            return True
        except Exception:
            return False

    def get_device_info(self) -> Dict[str, Any]:
        """获取OpenCL设备信息"""
        if not self.is_available():
            return {}

        try:
            return {
                "name": self.device.name,
                "vendor": self.device.vendor,
                "version": self.device.version,
                "global_memory": self.device.global_mem_size,
                "local_memory": self.device.local_mem_size,
                "compute_units": self.device.max_compute_units,
                "type": "OpenCL",
            }
        except Exception:
            return {}

    def test_passwords_batch(self, passwords: List[str], test_func) -> Optional[str]:
        """使用OpenCL批量测试密码"""
        # 类似CUDA，这里也需要根据具体算法实现
        return None


class NumbaAccelerator(GPUAccelerator):
    """Numba CUDA加速器"""

    def is_available(self) -> bool:
        """检查Numba CUDA是否可用"""
        if not NUMBA_CUDA_AVAILABLE:
            return False

        try:
            return numba_cuda.is_available()
        except Exception:
            return False

    def get_device_info(self) -> Dict[str, Any]:
        """获取Numba CUDA设备信息"""
        if not self.is_available():
            return {}

        try:
            device = numba_cuda.get_current_device()
            return {
                "name": device.name.decode("utf-8"),
                "compute_capability": device.compute_capability,
                "multiprocessor_count": device.MULTIPROCESSOR_COUNT,
                "warp_size": device.WARP_SIZE,
                "type": "Numba CUDA",
            }
        except Exception:
            return {}

    def test_passwords_batch(self, passwords: List[str], test_func) -> Optional[str]:
        """使用Numba CUDA批量测试密码"""
        return None


class GPUManager:
    """GPU管理器"""

    def __init__(self):
        self.accelerators = {
            "cuda": CUDAAccelerator(),
            "opencl": OpenCLAccelerator(),
            "numba": NumbaAccelerator(),
        }
        self.active_accelerator = None
        self.gpu_available = False
        self._detect_gpu()

    def _detect_gpu(self) -> None:
        """检测可用的GPU"""
        for name, accelerator in self.accelerators.items():
            if accelerator.is_available():
                self.active_accelerator = accelerator
                self.gpu_available = True
                print(f"检测到GPU加速器: {name}")
                break

        if not self.gpu_available:
            print("未检测到可用的GPU加速器")

    def is_gpu_available(self) -> bool:
        """检查GPU是否可用"""
        return self.gpu_available

    def get_gpu_info(self) -> Dict[str, Any]:
        """获取GPU信息"""
        if self.active_accelerator:
            return self.active_accelerator.get_device_info()
        return {}

    def get_available_accelerators(self) -> List[str]:
        """获取可用的加速器列表"""
        available = []
        for name, accelerator in self.accelerators.items():
            if accelerator.is_available():
                available.append(name)
        return available

    def test_passwords_with_gpu(self, passwords: List[str], test_func) -> Optional[str]:
        """使用GPU批量测试密码"""
        if not self.active_accelerator:
            return None

        return self.active_accelerator.test_passwords_batch(passwords, test_func)

    def cleanup(self) -> None:
        """清理GPU资源"""
        if self.active_accelerator and hasattr(self.active_accelerator, "cleanup"):
            self.active_accelerator.cleanup()

    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """获取系统信息"""
        info = {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "architecture": platform.architecture(),
            "cuda_available": CUDA_AVAILABLE,
            "opencl_available": OPENCL_AVAILABLE,
            "numba_cuda_available": NUMBA_CUDA_AVAILABLE,
        }

        # 检查NVIDIA驱动
        try:
            import subprocess

            result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
            info["nvidia_driver"] = result.returncode == 0
        except:
            info["nvidia_driver"] = False

        return info
