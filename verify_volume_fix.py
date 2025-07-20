#!/usr/bin/env python3
"""
验证分卷压缩包修复的完整性测试
"""

import os
import tempfile
import sys

# 添加项目路径到sys.path
sys.path.insert(0, os.path.dirname(__file__))

from core.archive_handler import ArchiveManager


def create_test_files():
    """创建测试用的假文件"""
    temp_dir = tempfile.mkdtemp()

    # 创建各种格式的测试文件
    test_files = [
        # 标准格式
        "test_standard.zip",
        "test_standard.7z",
        "test_standard.rar",
        # ZIP分卷
        "archive.zip",
        "archive.z01",
        "archive.z02",
        "archive.z03",
        # RAR分卷模式1
        "data.rar",
        "data.r00",
        "data.r01",
        # RAR分卷模式2
        "backup.part1.rar",
        "backup.part2.rar",
        "backup.part3.rar",
        # 7Z分卷
        "media.7z.001",
        "media.7z.002",
        "media.7z.003",
        # 不支持的格式
        "document.txt",
        "image.jpg",
        "video.mp4",
    ]

    for filename in test_files:
        filepath = os.path.join(temp_dir, filename)
        with open(filepath, "w") as f:
            f.write("test content")

    return temp_dir


def test_archive_manager():
    """完整测试ArchiveManager的分卷压缩包功能"""
    temp_dir = create_test_files()
    manager = ArchiveManager()

    print("=== 分卷压缩包支持修复验证 ===\n")

    # 测试用例
    test_cases = [
        # (文件名, 是否应该支持, 期望的格式类型, 期望的第一卷)
        ("test_standard.zip", True, ".zip", "test_standard.zip"),
        ("test_standard.7z", True, ".7z", "test_standard.7z"),
        ("test_standard.rar", True, ".rar", "test_standard.rar"),
        ("archive.z01", True, ".zip", "archive.zip"),
        ("archive.z02", True, ".zip", "archive.zip"),
        ("archive.z03", True, ".zip", "archive.zip"),
        ("data.r00", True, ".rar", "data.rar"),
        ("data.r01", True, ".rar", "data.rar"),
        ("backup.part2.rar", True, ".rar", "backup.part1.rar"),
        ("backup.part3.rar", True, ".rar", "backup.part1.rar"),
        ("media.7z.002", True, ".7z", "media.7z.001"),
        ("media.7z.003", True, ".7z", "media.7z.001"),
        ("document.txt", False, None, "document.txt"),
        ("image.jpg", False, None, "image.jpg"),
    ]

    print("1. 文件格式检测测试:")
    print("-" * 60)

    all_passed = True

    for filename, should_support, expected_type, expected_first_volume in test_cases:
        filepath = os.path.join(temp_dir, filename)

        # 测试是否支持
        is_supported = manager.is_supported(filepath)
        detected_type = manager._detect_archive_type(filepath)
        first_volume_path = manager._find_first_volume(filepath)
        first_volume_name = os.path.basename(first_volume_path)

        # 验证结果
        support_ok = is_supported == should_support
        type_ok = detected_type == expected_type
        first_volume_ok = first_volume_name == expected_first_volume

        status = "✓" if (support_ok and type_ok and first_volume_ok) else "✗"

        print(
            f"{status} {filename:<20} 支持:{is_supported:<5} 类型:{detected_type or 'None':<6} 第一卷:{first_volume_name}"
        )

        if not support_ok:
            print(
                f"    错误: 支持检测失败 (期望:{should_support}, 实际:{is_supported})"
            )
            all_passed = False
        if not type_ok:
            print(
                f"    错误: 类型检测失败 (期望:{expected_type}, 实际:{detected_type})"
            )
            all_passed = False
        if not first_volume_ok:
            print(
                f"    错误: 第一卷检测失败 (期望:{expected_first_volume}, 实际:{first_volume_name})"
            )
            all_passed = False

    print(f"\n2. 文件对话框过滤器测试:")
    print("-" * 60)

    filter_str = manager.get_supported_formats_filter()
    print(f"过滤器字符串: {filter_str}")

    # 检查过滤器是否包含分卷格式
    expected_patterns = ["*.z*", "*.r*", "*.part*.rar", "*.7z.*"]
    filter_ok = all(pattern in filter_str for pattern in expected_patterns)

    if filter_ok:
        print("✓ 文件过滤器包含所有分卷格式")
    else:
        print("✗ 文件过滤器缺少分卷格式")
        all_passed = False

    print(f"\n3. 压缩文件信息获取测试:")
    print("-" * 60)

    # 测试分卷文件的信息获取
    volume_test_files = ["archive.z02", "data.r01", "backup.part2.rar", "media.7z.002"]

    for filename in volume_test_files:
        filepath = os.path.join(temp_dir, filename)
        info = manager.get_archive_info(filepath)

        if "error" in info:
            print(f"✗ {filename:<20} 错误: {info['error']}")
            all_passed = False
        else:
            is_volume = info.get("is_volume", False)
            status = "✓" if is_volume else "✗"
            print(f"{status} {filename:<20} 分卷标识: {is_volume}")
            if is_volume:
                first_volume = info.get("first_volume", "")
                if first_volume:
                    print(f"    第一卷: {os.path.basename(first_volume)}")

    # 清理临时文件
    import shutil

    shutil.rmtree(temp_dir)

    print(f"\n=== 测试结果 ===")
    if all_passed:
        print("✓ 所有测试通过！分卷压缩包支持修复成功。")
        return True
    else:
        print("✗ 部分测试失败，需要进一步检查。")
        return False


if __name__ == "__main__":
    success = test_archive_manager()

    if success:
        print("\n现在程序应该能够正确处理以下类型的分卷压缩包:")
        print("- ZIP分卷: file.zip, file.z01, file.z02, ...")
        print(
            "- RAR分卷: file.rar, file.r00, file.r01, ... 或 file.part1.rar, file.part2.rar, ..."
        )
        print("- 7Z分卷: file.7z.001, file.7z.002, ...")
        print("\n用户可以拖拽任意分卷到程序中，程序会自动找到第一卷进行处理。")

    sys.exit(0 if success else 1)
