from flask import Flask
import logging
from bin.export import Is_program_running
import sys
import os

def resource_path(relative_path):
    """获取打包后的资源路径"""
    try:
        # PyInstaller打包后的临时文件路径
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

app = Flask(
    __name__,
    template_folder=resource_path('templates')  # 动态指定模板路径
)
app.secret_key = 'pcsmt2'

if Is_program_running.IsProgramExe():
    log = logging.getLogger('werkzeug')
    log.disabled = True  # 禁用请求日志

def run_flask():
    # TODO: 添加端口参数,以便用户自行配置
    from . import api, api_server, api_program, PageServer, PageProgram
    app.run(port=5000)