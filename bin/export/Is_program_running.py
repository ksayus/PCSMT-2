import os
import json
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
                print(psutil.Process(pid).name())
                counts += 1
    except Exception as e:
        print(e)

    return counts

if  __name__ == '__main__':
    print(os.getpid())