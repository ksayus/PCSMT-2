from bin.export import log
import requests
import subprocess
import os

def install_java_windows(version):
    try:
        if version == 8:
            url = "https://javadl.oracle.com/webapps/download/AutoDL?BundleId=248242_ce59cff5c23f4e2eaf4e778a117d4c5b"
        elif version == 17:
            url = "https://download.oracle.com/java/17/latest/jdk-17_windows-x64_bin.exe"
        elif version == 21:
            url = "https://download.oracle.com/java/21/latest/jdk-21_windows-x64_bin.exe"
        else:
            log.logger.error("不支持的Java版本")
            return

        # 下载安装包
        installer_path = f"jdk{version}_installer.exe"
        response = requests.get(url, headers={"Cookie": "oraclelicense=accept-securebackup-cookie"})
        with open(installer_path, "wb") as f:
            f.write(response.content)

        # 静默安装
        subprocess.run([installer_path, "/s"], check=True)
        os.remove(installer_path)  # 删除安装包
        log.logger.info("安装完成！请手动配置环境变量JAVA_HOME和PATH。")
        return True
    except Exception as e:
        log.logger.error(f"安装失败: {e}")
        return False