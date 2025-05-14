from flask import Flask
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

def run_flask():
    from . import api, api_server, api_program
    app.run(port=5000)