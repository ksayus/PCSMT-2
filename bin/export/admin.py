from bin.find_files import find_file
from bin.find_files import find_folder
from bin.export import log
from bin.export import key

def examin_admin_account_is_exist(account_name=None):
    """
    检查管理员账户文件完整性
    :param account_name: 管理员账户名称
    :return: False(错误) or True(正确)
    """
    if find_folder.find_folders_with_existence("C:\PCSMT2-key\\account"):
        if account_name == None:
            #遍历管理员账户文件夹,并检查每个账户的完整性
            accounts = find_file.find_files_with_extension("C:\PCSMT2-key\\account", ".bin")
            if accounts != None:
                for account_name in accounts:
                    # 只填入管理员账户名称
                    # 需要将account_name的路径处理成只有名称
                    account_name = account_name.split("\\")[-1].split(".")[0]
                    if examin_admin_account_is_exist(account_name):
                        pass
                    else:
                        log.logger.error('管理员账户文件不完整！')
                        return False
                return True
            else:
                log.logger.error('没有管理员账户！')
                return False
        else:
            if find_file.find_files_with_existence("C:\PCSMT2-key\\account\\" + account_name + ".bin"):
                try:
                    with open("C:\PCSMT2-key\\account\\" + account_name + ".bin", "rb") as f:
                        if not f.read():
                            log.logger.error(f'账户 {account_name} 文件为空！')
                            return False
                        return True
                except:
                    log.logger.error('管理员账户文件读取失败！')
                    return False
            else:
                log.logger.error('管理员账户文件不存在！')
                return False
    else:
        log.logger.error('管理员账户文件不存在！')
        return False

def set_admin_account(account, password):
    """
    设置管理员账户
    :param account: 管理员账户名称
    :param password: 管理员密码
    :return: False(错误) or True(正确)
    """
    if find_folder.find_folders_with_existence_and_create("C:\PCSMT2-key\\account"):
        if examin_admin_account_is_exist(account):
            log.logger.error('管理员账户文件已存在！')
            return False
        else:
            try:
                with open("C:\PCSMT2-key\\account\\" + account + ".bin", "wb") as f:
                    password = key.cipher_key(password)
                    f.write(password)
            except Exception as e:
                log.logger.error('管理员账户文件写入失败！')
                log.logger.error(e)
                return False
    else:
        log.logger.error('创建管理员账户文件失败！')
        return False

def examin_admin_account(account, password):
    """
    检查管理员账户
    :param account: 管理员账户名称
    :param password: 管理员密码
    :return: False(错误) or True(正确)
    """
    if examin_admin_account_is_exist(account):
        try:
            with open("C:\PCSMT2-key\\account\\" + account + ".bin", "rb") as f:
                password_plain = key.decipher_key(f.read())
                if password == password_plain:
                    return True
                else:
                    return False
        except Exception as e:
            log.logger.error('管理员账户文件读取失败！')
            log.logger.error(e)
            return False
    else:
        log.logger.error('管理员账户文件不存在！')
        return False