import os
from bin.export import log

def find_files_with_extension(directory, extension):
    """
    在指定目录中查找指定后缀名的文件
    :param directory: 要搜索的目录
    :param extension: 文件后缀名（例如 '.txt'）
    :return: 匹配的文件列表
    """
    matched_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                matched_files.append(os.path.join(root, file))
    return matched_files

def find_files_with_existence_and_create(directory):
    """
    在指定目录中查找指定的文件
    若不存在则自动创建该文件的空文件
    :param directory: 要搜索的目录
    :return: 匹配的文件列表
    """
    if os.path.exists(directory):
        # log.logger.info("文件存在:" + directory)
        return True
    else:
        # log.logger.info("文件不存在，创建文件:" + directory)
        try:
            with open(directory, 'w') as file:
                file.close()
            return True
        except OSError:
            log.logger.error("创建文件失败")
            return False

def find_files_with_existence(directory ,msg=True):
    """
    在指定目录中查找指定的文件
    若不存在则返回False
    """
    if os.path.exists(directory):
        # log.logger.info("文件存在:" + directory)
        return True
    else:
        if msg:
            log.logger.error("文件不存在:" + directory)
        return False

def find_keyword_inline_and_change_argument(file_path, keyword, argument):
    """
    在指定文件中查找指定的关键字并替换为指定的参数
    :param file_path: 要搜索的文件路径
    :param keyword: 要搜索的关键字
    :param argument: 要替换的参数
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        print(f"无法使用 utf-8 解码文件 {file_path}，尝试使用 ISO-8859-1 编码...")
        try:
            with open(file_path, 'r', encoding='ISO-8859-1') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            print(f"无法使用 ISO-8859-1 解码文件 {file_path}，跳过文件...")
            return

    modified = False
    matched_lines = []
    for line_number, line in enumerate(lines, start=1):
        if keyword in line:
            matched_lines.append((line_number, line))
            lines[line_number - 1] = keyword + '=' + argument + '\n'
            modified = True

    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        log.logger.info(f"文件 {file_path} 中的 {keyword} 已替换为 {argument}")
    else:
        log.logger.error(f"文件 {file_path} 中未找到 {keyword}")

    for line_number, line in matched_lines:
        log.logger.debug(f"匹配到行 {line_number}: {line.strip()}")