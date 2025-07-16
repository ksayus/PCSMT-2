import requests
import os
import urllib3
from bin.export import log
from bin.export import Info
from packaging import version
from bin.command import Program

class Source:
    def Github():
        """
        检查更新 github
        :return: bool
        """
        # 检查更新
        log.logger.info("正在检查更新...")
        try:
            urllib3.disable_warnings()
            response = requests.get(Info.ProjectRepository.Github, verify=False)
            response_json = response.json()
            latest_version_str = response_json['tag_name']
            latest_version = response_json['name']

            #latest_version_str = latest_version.replace('PCSMT-v', '')

            log.Debug(Info.Config.Config['PCSMT2_Version'])
            log.Debug(latest_version_str)

            try:

                v1 = version.parse(Info.Config.Config['PCSMT2_Version'])
                v2 = version.parse(latest_version_str)

                if v1 == v2:
                    log.logger.info("当前版本已是最新版本，无需更新。")
                    return True
                elif v1 < v2:
                    log.logger.info("检测到新版本!")
                    log.logger.info("最新版本为：" + latest_version)
                    log.logger.info("尝试更新...")
                    # 获取最新版本号和下载地址
                    try:
                        download_url = response_json['assets'][0]['browser_download_url']
                        log.logger.info("正在下载文件...")
                        log.logger.debug("下载url:" + download_url)
                        # 下载更新文件
                        try:
                            os.system('powershell curl -o "' + Info.work_path + '/' + latest_version + '.exe' '" ' + download_url)
                            log.logger.info("文件下载成功。")
                            log.logger.info("请重启程序以完成更新。")
                            Program.Do.CreateShortCut(latest_version, True)
                            Program.Processing.Restart(latest_version)
                            return
                        except Exception as e:
                            log.logger.error("文件下载失败，请检查网络连接。")
                            log.logger.error(e)
                            return
                    except Exception as e:
                        log.logger.error("获取更新信息失败，请检查网络连接。")
                        log.logger.error(e)
                        return False

                else:
                    log.logger.info("当前版本已是最新版本，无需更新。")
                    return

            except Exception as e:
                log.logger.error("版本号解析失败，请检查版本号格式。")
                log.logger.error(e)
                return False

        except requests.exceptions.RequestException as e:
            log.logger.error("网络连接失败，请检查网络连接。")
            log.logger.error(e)
            return False

    def Gitee():
        """
        检查更新 gitee
        :return: bool
        """
        # 检查更新
        log.logger.info("正在检查更新...")
        try:
            response = requests.get(Info.ProjectRepository.Gitee)
            response_json = response.json()
            latest_version_str = response_json['tag_name']
            latest_version = response_json['name']

            # latest_version_str = latest_version.replace('PCSMT-v', '')

            log.Debug(Info.Config.Config['PCSMT2_Version'])
            log.Debug(latest_version_str)

            try:

                v1 = version.parse(Info.Config.Config['PCSMT2_Version'])
                v2 = version.parse(latest_version_str)

                if v1 == v2:
                    log.logger.info("当前版本已是最新版本，无需更新。")
                    return True
                elif v1 < v2:
                    log.logger.info("检测到新版本!")
                    log.logger.info("最新版本为：" + latest_version)
                    # 获取最新版本号和下载地址
                    try:
                        log.Debug("获取下载url")
                        latest_assets = response_json['assets']
                        for asset in latest_assets:
                            if asset['name'].endswith('.exe'):
                                download_url = asset['browser_download_url']
                                break

                        if download_url is None:
                            log.logger.error("未找到匹配的 .exe 文件，请检查版本信息。")
                            return False

                        log.logger.info("尝试更新...")
                        log.logger.info("正在下载文件...")
                        log.Debug("下载url:" + download_url)
                        # 下载更新文件
                        try:
                            os.system('powershell curl -o ' + Info.work_path + '/' + latest_version + '.exe ' + download_url)
                            log.logger.info("文件下载成功。")
                            log.logger.info("请重启程序以完成更新。")
                            Program.Do.CreateShortCut(latest_version, True)
                            Program.Processing.Restart(latest_version)
                            return
                        except Exception as e:
                            log.logger.error("文件下载失败，请检查网络连接。")
                            log.logger.error(e)
                            return
                    except Exception as e:
                        log.logger.error("获取更新信息失败，请检查网络连接。")
                        log.logger.error(e)
                        return False

                else:
                    log.logger.info("当前版本已是最新版本，无需更新。")
                    return

            except Exception as e:
                log.logger.error("版本号解析失败，请检查版本号格式。")
                log.logger.error(e)
                return False

        except requests.exceptions.RequestException as e:
            log.logger.error("网络连接失败，请检查网络连接。")
            log.logger.error(e)
            return False