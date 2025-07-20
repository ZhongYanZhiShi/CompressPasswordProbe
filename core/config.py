"""
配置管理模块
"""

import os
import json
from typing import Dict, Any, Optional


class Config:
    """应用程序配置管理类"""

    def __init__(self):
        self.config_file = "config.json"
        self.default_config = {
            "gpu_acceleration": False,
            "max_threads": 4,
            "max_attempts": 0,  # 0表示无限制
            "timeout_seconds": 0,  # 0表示无限制
            "last_dictionary_path": "",
            "last_archive_path": "",
            "save_log": True,
            "log_directory": "logs",
            "ui_language": "zh_CN",
            "batch_size": 1000,  # GPU批处理大小
            "auto_detect_gpu": True,
        }
        self.config = self.default_config.copy()
        self.load_config()

    def load_config(self) -> None:
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
        except Exception as e:
            print(f"加载配置文件失败: {e}")

    def save_config(self) -> None:
        """保存配置文件"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置文件失败: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """设置配置项"""
        self.config[key] = value

    def update(self, updates: Dict[str, Any]) -> None:
        """批量更新配置"""
        self.config.update(updates)

    def reset_to_default(self) -> None:
        """重置为默认配置"""
        self.config = self.default_config.copy()

    def get_log_directory(self) -> str:
        """获取日志目录路径"""
        log_dir = self.get("log_directory", "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        return log_dir
