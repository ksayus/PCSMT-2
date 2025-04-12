import os
import atexit
import sys

Lock_File = os.getcwd() + '/Lock_File.lock'

def Is_program_running():
    """检查程序是否正在运行"""
    if os.path.exists(Lock_File):
        print("程序正在运行中，关闭程序！")
        sys.exit()
    else:
        with open(Lock_File, "w") as f:
            f.write("This file is used to prevent multiple instances.")
            atexit.register(Remove_Lock_File)
        print("程序已被锁定,不可多次启动！")

def Remove_Lock_File():
    """删除锁文件"""
    if os.path.exists(Lock_File):
        os.remove(Lock_File)