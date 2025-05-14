import os
import json
import psutil
def exist_program_is_running():
    pids = psutil.pids()
    pid_lists = []
    counts = 0
    try:
        # 获取版本号
        with open("./config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
            f.close()

        for pid in pids:
            p = psutil.Process(pid)
            pid_lists.append(p.name())
            s = str(p.name())
            if s == 'PCSMT2-v' + config['PCSMTVersion'] + '.exe':
                print(s)
                counts += 1
    except Exception as e:
        print(e)

    return counts