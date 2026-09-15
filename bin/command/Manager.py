import os
import shutil
import time
from bin.find_files.tree import Tree
from bin.export import log

# 管理文件
class Manager:
    class File:
        # 删除文件
        def Delete(self, file_path: str):
            os.remove(file_path)
            log.logger.info(f'删除文件: {file_path}')

            return True

        # 移动文件
        def Move(self, current_file_path: str, target_file_path: str):
            shutil.move(current_file_path, target_file_path)
            log.logger.info(f'移动文件: {current_file_path} -> {target_file_path}')

            return True

        # 复制文件
        def Copy(self, current_file_path: str, target_file_path: str):
            shutil.copy(current_file_path, target_file_path)
            log.logger.info(f'复制文件: {current_file_path} -> {target_file_path}')

            return True

        # 重命名文件
        def Rename(self, current_file_path: str, target_file_path: str):
            os.rename(current_file_path, target_file_path)
            log.logger.info(f'重命名文件: {current_file_path} -> {target_file_path}')

            return True

        # 搜索文件
        def Search(self, file_path: str, file_name: str):
            tree = Tree(file_path).GetTree()
            self.search_result = []
            for file in tree:
                if file_name in file:
                    log.logger.info(f'找到文件: {file_name}')
                    self.search_result.append(file)
                else:
                    log.logger.info(f'未找到文件: {file_name}')

            log.Debug(f'搜索结果: {self.search_result}')

            return self.search_result

        # 创建文件
        def Create(self, file_path: str):
            with open(file_path, 'w') as f:
                pass
            log.logger.info(f'创建文件: {file_path}')

            return True

        # 获取文件状态
        def Status(self, file_path: str):
            self.file_stat = os.stat(file_path)
            mod_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.file_stat.st_mtime))
            self.file_stat_info = {
                'size': self.file_stat.st_size,
                'mod_time': mod_time,
            }
            log.Debug(f'文件状态: {self.file_stat_info}')

            return self.file_stat_info

    class Folder:
        # 删除文件夹
        def Delete(self, folder_path: str):
            shutil.rmtree(folder_path)
            log.logger.info(f'删除文件夹: {folder_path}')

            return True

        # 创建文件夹
        def Create(self, folder_path: str):
            os.makedirs(folder_path)
            log.logger.info(f'创建文件夹: {folder_path}')

            return True

        # 获取文件夹状态
        def Status(self, folder_path: str):
            self.folder_stat = os.stat(folder_path)
            mod_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.folder_stat.st_mtime))
            self.folder_stat_info = {
                'size': self.folder_stat.st_size,
                'mod_time': mod_time,
            }
            log.Debug(f'文件夹状态: {self.folder_stat_info}')

            return self.folder_stat_info

        # 重命名文件夹
        def Rename(self, folder_path: str, target_folder_path: str):
            os.rename(folder_path, target_folder_path)
            log.logger.info(f'重命名文件夹: {folder_path} -> {target_folder_path}')

            return True

        # 复制文件夹
        def Copy(self, folder_path: str, target_folder_path: str):
            shutil.copytree(folder_path, target_folder_path)
            log.logger.info(f'复制文件夹: {folder_path} -> {target_folder_path}')

            return True

        # 移动文件夹
        def Move(self, folder_path: str, target_folder_path: str):
            shutil.move(folder_path, target_folder_path)
            log.logger.info(f'移动文件夹: {folder_path} -> {target_folder_path}')

            return True