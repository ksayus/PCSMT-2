import os
from pathlib import Path

class Tree:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.path = Path(self.root_dir)
        self.tree = []

    def GetTree(self):
        """
        获取目录树
        :return: 目录树
        """
        for file in self.path.rglob('*'):
            self.tree.append(str(file))

        return self.tree

    def CurrentTree(self):
        """
        获取当前目录树
        :return: 当前目录树
        """
        self.tree = os.listdir(self.root_dir)
        return self.tree
