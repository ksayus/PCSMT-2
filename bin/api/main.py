from flask import Flask
import logging
from bin.export import IsProgramRunning
from bin.export import Info
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
    template_folder=resource_path('templates'),  # 动态指定模板路径
    static_folder=resource_path('static')       # 动态指定静态资源路径
)
app.secret_key = 'pcsmt2'

if IsProgramRunning.Is.Running():
    log = logging.getLogger('werkzeug')
    log.disabled = True  # 禁用请求日志

def run_flask():
    from . import api, api_server, api_program, PageServer, PageProgram, Resouce, ServerSocket
    app.run(port = Info.Config.Port())
