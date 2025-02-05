import os
from bin.export import log

def examin_java_exist():
    try:
        os.system('java --version')
        return True
    except Exception as e:
        log.logger.error(e)
        return False