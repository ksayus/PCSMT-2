import os
import sys
import psutil
import win32process
import win32gui

class Is:
    def Running():
        pids = psutil.pids()
        pid_lists = []
        counts = 0
        try:
            # 获取当前程序名称
            program_pid = os.getpid() # pid
            pName = psutil.Process(program_pid).name() #name

            for pid in pids:
                p = psutil.Process(pid)
                pid_lists.append(p.name())
                s = str(p.name())
                if s == pName:
                    if Is.ProgramExe() != True:
                        pass
                        # print(psutil.Process(pid).name())
                    counts += 1
        except Exception as e:
            print(e)

        return counts

    def ProgramExe():
        """
        判断程序是否为exe文件
        True: 是exe文件
        False: 不是exe文件

        :return: True or False
        """
        # 检查是否存在 '_MEIPASS' 属性（资源目录）或 'frozen' 属性
        return hasattr(sys, '_MEIPASS') or getattr(sys, 'frozen', False)

class Do:
    def taskkill(Name, typeName):
        """
        用于结束指定进程
        Name: 进程名称
        typeName: 进程类型名称
        示例:
        IsProgramRunning.Do.taskkill(server_name, "cmd.exe")
        """
        windows_list = []
        win32gui.EnumWindows(lambda hWnd, param: param.append(hWnd), windows_list)
        for window in windows_list:
            title = win32gui.GetWindowText(window)
            if f'{Name}' in title:
                if f'{typeName}' not in title:  # 忽略cmd窗口
                    pass
                else:
                    # print(f'title:{title}')
                    # 获取窗口对应的进程ID
                    _, pid = win32process.GetWindowThreadProcessId(window)
                    # print(f'pid:{pid}')
                    # kill process
                    os.system(f'taskkill /F /PID {pid}')