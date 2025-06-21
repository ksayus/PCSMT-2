import os
import sys
import psutil
def exist_program_is_running():
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
                if IsProgramExe() != True:
                    print(psutil.Process(pid).name())
                counts += 1
    except Exception as e:
        print(e)

    return counts

def IsProgramExe():
    # 检查是否存在 '_MEIPASS' 属性（资源目录）或 'frozen' 属性
    return hasattr(sys, '_MEIPASS') or getattr(sys, 'frozen', False)

if  __name__ == '__main__':
    print(os.getpid())