<<<<<<< HEAD
import os
from bin.export import log

def examin_java_exist():
    try:
        os.system('java --version')
        return True
    except Exception as e:
        log.logger.error(e)
=======
import os
from bin.export import log

def examin_java_exist():
    try:
        os.system('java --version')
        return True
    except Exception as e:
        log.logger.error(e)
>>>>>>> 6c0b95ef8a36d5d56bb1e47e255c35b967a128a8
        return False