import subprocess
import re
import os
from pathlib import Path
from typing import List, Dict, Union
from bin.export import log
import json
from bin.export import get
from bin.export import program_info
from bin.export import size_change

def find_java_installations():
    """自动扫描系统常见Java安装路径"""
    java_paths = set()

    # 根据不同操作系统扫描路径
    if os.name == 'nt':  # Windows
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        java_dirs = Path(program_files) / "Java"
        if java_dirs.exists():
            for entry in java_dirs.iterdir():
                java_exe = entry / "bin" / "java.exe"
                if java_exe.exists():
                    java_paths.add(str(java_exe))
    else:
        common_paths = [
            "/usr/lib/jvm",
            "/usr/java",
            "/Library/Java/JavaVirtualMachines",  # macOS
            str(Path.home() / ".sdkman/candidates/java/current/bin/java")  # SDKMAN安装
        ]
        for path in common_paths:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    if "java" in files:
                        java_path = Path(root) / "java"
                        java_paths.add(str(java_path))

    return list(java_paths)

def get_java_version(java_path: str) -> Union[str, None]:
    """获取指定Java路径的版本"""
    try:
        result = subprocess.run(
            [java_path, '-version'],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            check=True,
            timeout=5
        )
        output = result.stderr

        # 匹配两种常见版本格式：
        # 1. 旧格式: "1.8.0_391"
        # 2. 新格式: "21.0.2" 或 "21.0.2+13-LTS"
        version_match = re.search(
            r'version "(\d+\.\d+\.\d+[_\+\-]?.*?)"', 
            output
        )
        return version_match.group(1) if version_match else None
    except Exception as e:
        return None

def parse_version(version_str: Union[str, int]) -> List[int]:
    """将版本字符串或整型转换为可比较的数字列表"""
    # 添加类型转换
    version_str = str(version_str)  # 确保输入为字符串类型
    # 清理特殊字符并分割版本号（保持原有逻辑）
    clean_version = re.sub(r'[^0-9.]', '', version_str.split('+')[0])
    return [int(num) for num in clean_version.split('.') if num.isdigit()]

def is_version_match(
    target: str,
    installed: str,
    exact_match: bool = False
) -> bool:
    """版本号匹配逻辑"""
    target_ver = parse_version(target)
    installed_ver = parse_version(installed)

    # 精确匹配模式
    if exact_match:
        return installed.startswith(target)

    # 主版本匹配模式（例如输入11匹配11.x.x）
    min_length = min(len(target_ver), len(installed_ver))
    return target_ver[:min_length] == installed_ver[:min_length]

def examin_java_exist(
    target_version: Union[str, int],
    exact_match: bool = False,
    custom_paths: List[str] = None
) -> Dict[str, str]:
    """
    检查指定Java版本是否安装

    :param target_version: 要检查的目标版本（如"1.8"或"17"）
    :param exact_match: 是否精确匹配完整版本号
    :param custom_paths: 自定义检查路径列表
    :return: 字典 {安装路径: 版本}
    """
    target_version = str(target_version)
    found_versions = {}

    # 扫描所有Java安装
    all_paths = find_java_installations()
    if custom_paths:
        all_paths += [os.path.expanduser(p) for p in custom_paths]

    for path in all_paths:
        if not os.path.exists(path):
            continue

        version = get_java_version(path)
        if version and is_version_match(target_version, version, exact_match):
            found_versions[path] = version

    return found_versions

def ServerInfoKeys(server_name):
    """
    检查服务器信息json文件
    :param server_name: 服务器名称
    :return: False(错误) or server_info(正确)
    """
    try:
        with open(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json', 'r', encoding='utf-8') as f:
            server_info = json.load(f)
            f.close()
            if not 'server_name' in server_info:
                log.logger.error('服务器信息文件缺少server_name字段！')
                server_info['server_name'] = server_name
            if not 'start_count' in server_info:
                log.logger.error('服务器信息文件缺少start_count字段！')
                server_info['start_count'] = 0
            if not 'server_core' in server_info:
                log.logger.error('服务器信息文件缺少server_core字段！')
                server_info['server_core'] = 'N/A'
            if not 'server_path' in server_info:
                log.logger.error('服务器信息文件缺少server_path字段！')
                server_info['server_path'] = 'N/A'
            if not 'server_start_batch_path' in server_info:
                log.logger.error('服务器信息文件缺少server_start_batch_path字段！')
                server_info['server_start_batch_path'] = 'N/A'
            if not 'server_version' in server_info:
                log.logger.error('服务器信息文件缺少server_version字段！')
                server_info['server_version'] = 'N/A'
            server_info['server_size'] = size_change.size_change(get.get_dir_size(server_info['server_path']))
        with open(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json', 'w', encoding='utf-8') as f:
            json.dump(server_info, f, indent=4)
            f.close()
        return server_info
    except Exception as e:
        log.logger.error('读取服务器信息失败！')
        log.logger.error(e)
        return False