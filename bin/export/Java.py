import zipfile
import requests
import subprocess
import os
import sys
import platform
import time
import ctypes
from tqdm import tqdm
from bin.export import log

class Install:
    def Windows(version):
        try:
            def SerJavaEnviroment(jdk_path, version):
                try:
                    if platform.system() == "Windows":
                        subprocess.run(f'setx JAVA_HOME "{jdk_path}" /M', shell=True, check=True)
                        subprocess.run(f'setx PATH "%PATH%;{jdk_path}\\bin" /M', shell=True, check=True)
                        log.logger.info("环境变量配置成功")
                        return True
                    else:
                        return False  # 当前仅支持Windows
                except Exception as e:
                    log.logger.error(f"设置环境变量失败: {str(e)}")
                    return False

            if os.name == 'nt':
                if ctypes.windll.shell32.IsUserAnAdmin() == 0:
                    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
                    sys.exit()

            if not ctypes.windll.shell32.IsUserAnAdmin():
                log.logger.error("请以管理员身份运行本程序")
                input("按任意键继续...")
                sys.exit()

            if version == 1.8:
                url = "https://corretto.aws/downloads/latest/amazon-corretto-8-x64-windows-jdk.zip"
            elif version == 16:
                url = "https://corretto.aws/downloads/latest/amazon-corretto-16-x64-windows-jdk.zip"
            elif version == 17:
                url = "https://corretto.aws/downloads/latest/amazon-corretto-17-x64-windows-jdk.zip"
            elif version == 21:
                url = "https://corretto.aws/downloads/latest/amazon-corretto-21-x64-windows-jdk.zip"
            else:
                log.logger.error("不支持的Java版本")
                return

            installer_path = os.path.join(os.environ["TEMP"], f"jdk{version}_installer.zip")  # 修改文件扩展名为zip
            max_retries = 5
            download_success = False
            last_error = None

            for attempt in range(max_retries):
                try:
                    current_url = url
                    log.logger.info(f"尝试从 {current_url} 下载JDK安装包 (尝试 {attempt + 1}/{max_retries})")

                    with requests.get(current_url,
                                    headers={
                                        "Cookie": "oraclelicense=accept-securebackup-cookie",
                                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                                    },
                                    stream=True,
                                    timeout=60) as response:
                        response.raise_for_status()
                        total_size = int(response.headers.get('content-length', 0))
                        downloaded_size = 0

                        with open(installer_path, "wb") as f:
                            with tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024, desc="正在下载") as pbar:
                                for chunk in response.iter_content(chunk_size=8192):
                                    f.write(chunk)
                                    pbar.update(len(chunk))

                        if total_size > 0 and os.path.getsize(installer_path) != total_size:
                            raise Exception("下载文件大小不匹配")

                        download_success = True
                        break
                except Exception as e:
                    last_error = str(e)
                    log.logger.warning(f"下载失败: {last_error}")
                    if os.path.exists(installer_path):
                        try:
                            os.remove(installer_path)
                        except:
                            pass
                    time.sleep(10)

            if not download_success:
                log.logger.error(f"所有下载源均失败，最后错误信息: {last_error}")
                return False

            installer_abs_path = os.path.abspath(installer_path)
            log.logger.debug(f"安装包绝对路径：{installer_abs_path}")

            if not os.path.exists(installer_abs_path):
                log.logger.error(f"安装包不存在，请检查下载路径")
                return False

            max_retries = 3
            parent_dir = r'C:\Program Files\Java'  # 删除原install_dir设置，改为固定路径
            os.makedirs(parent_dir, exist_ok=True)

            # 将解压逻辑移到所有版本共用的代码块
            try:
                log.logger.info("开始解压JDK安装包...")
                os.makedirs(parent_dir, exist_ok=True)

                with zipfile.ZipFile(installer_abs_path, 'r') as zip_ref:
                    zip_ref.extractall(parent_dir)

                extracted_dirs = [
                    d for d in os.listdir(parent_dir)
                    if os.path.isdir(os.path.join(parent_dir, d))
                ]

                log.logger.debug(f"所有顶层目录列表：{extracted_dirs}")

                if not extracted_dirs:
                    raise Exception("解压后无目录生成")

                if len(extracted_dirs) != 1:
                    log.logger.warning(f"检测到多个顶层目录({len(extracted_dirs)})，按修改时间选择最新目录")
                    extracted_dirs.sort(key=lambda x: os.path.getmtime(os.path.join(parent_dir, x)), reverse=True)

                actual_jdk_dir = os.path.join(parent_dir, extracted_dirs[0])
                log.logger.info(f"选定JDK目录：{actual_jdk_dir}")

                latest_jdk = actual_jdk_dir  # 确保所有版本都赋值latest_jdk变量
            except Exception as zip_e:
                log.logger.error(f"解压失败: {zip_e}", exc_info=True)
                return False

            # 补充：在验证阶段增加路径存在性检查
            try:
                required_files = ["bin/java.exe", "bin/javac.exe"]
                if not all(os.path.exists(os.path.join(latest_jdk, f)) for f in required_files):
                    raise Exception(f"关键文件缺失：{[f for f in required_files if not os.path.exists(os.path.join(latest_jdk, f))]}")
            except Exception as verify_e:
                log.logger.error(f"文件验证失败: {verify_e}", exc_info=True)
                return False

            # 补充：在验证阶段增加路径存在性检查后新增版本验证
            try:
                java_path = os.path.join(latest_jdk, 'bin', 'java.exe')
                result = subprocess.run([java_path, '-version'],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                text=True)
                if result.returncode != 0:
                    raise Exception(f"Java版本验证失败：{result.stdout}")
                log.logger.info(f"Java版本验证成功：{result.stdout.strip()}")
            except Exception as e:
                log.logger.error(f"Java版本验证失败: {e}")
                return False

            try:
                if not SerJavaEnviroment(latest_jdk, version):
                    log.logger.warning("环境变量配置失败，但安装验证已通过")
            except Exception as env_e:
                log.logger.error(f"环境变量配置异常: {env_e}")

            log.logger.info("Java安装及验证全部通过")
            log.logger.info("Java安装成功。请重新启动终端或以管理员身份运行命令提示符以使环境变量生效。")  # 新增提示信息
            return java_path

        except Exception as e:
            log.logger.error(f"安装失败: {e}", exc_info=True)
            try:
                os.remove(installer_path)
            except Exception:
                pass
            return False