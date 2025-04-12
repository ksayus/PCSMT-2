from flask import Flask, jsonify, request, render_template
from bin.command import server
from bin.export import program_info
from bin.export import log
from bin.find_files import find_file
import json
import sys
import os
from bin.export import admin
from flask import session, redirect, url_for

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

@app.route('/', methods=['GET'])
def api_root():
    return '<h1>Welcome to PCSMT2 API!</h1>'


# server
@app.route('/server', methods=['GET'])
def server_api_root():
    return '<h1>Welcome to PCSMT2 Server API!</h1>'

@app.route('/server/list', methods=['GET'])
def server_lists():
    try:
        # 使用 jsonify 返回 JSON 格式的响应
        return jsonify(program_info.server_list)
    except Exception as e:
        # 记录错误日志（建议使用 logging 模块）
        # 返回 JSON 格式的错误信息和 500 状态码
        log.logger.error('获取服务器列表时发生内部错误')
        return jsonify({"error": "获取服务器列表时发生内部错误"}), 500

@app.route('/server/<string:server_name>', methods=['GET'])
def server_info(server_name):
    try:
        server_info = server.search_server(server_name)
        if server_info == False:
            log.logger.error('服务器不存在')
            return jsonify({"error": "服务器不存在"}), 404
        else:
            return jsonify(server_info)
    except Exception as e:
        # 记录错误日志（建议使用 logging 模块）
        # 返回 JSON 格式的错误信息和 500 状态码
        log.logger.error('获取服务器信息时发生内部错误')
        return jsonify({"error": "获取服务器信息时发生内部错误"}), 500

@app.route('/server/latest', methods=['GET'])
def start_latest_server():
    try:
        server_lists = find_file.find_files_with_existence(program_info.work_path + program_info.program_resource + program_info.latest_start_server_json)
        if server_lists == False:
            log.logger.error('未找到服务器，请检查服务器名称是否正确！')
            return False
        else:
            with open(program_info.work_path + program_info.program_resource + program_info.latest_start_server_json, 'r', encoding='utf-8') as f:
                server_info = json.load(f)
                f.close()
        return jsonify(server_info)
    except Exception as e:
        # 记录错误日志（建议使用 logging 模块）
        # 返回 JSON 格式的错误信息和 500 状态码
        log.logger.error('启动服务器时发生内部错误')
        return jsonify({"error": "启动服务器时发生内部错误"}), 500

def admin_required(f):
    def wrapper(*args, **kwargs):
        if 'authenticated' not in session:  # 修改为登录时设置的键名
            return jsonify({"error": "未认证, 请前往 http://127.0.0.1:5000/login 登录!"}), 401
        return f(*args, **kwargs)
    return wrapper

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        account = request.form.get('admin_account')
        password = request.form.get('admin_password')

        if admin.examin_admin_account(account, password):
            session['authenticated'] = True  # 此处依赖secret_key
            return redirect(url_for('server_api_root'))
        else:
            return render_template('login.html', error="账号或密码错误")
    return render_template('login.html')


@app.route('/server/<string:server_name>/start', methods=['GET'])
@admin_required  # ✅ 添加认证装饰器
def start_server(server_name):
    try:
        success = server.start_server(server_name)
        if success:
            return jsonify({"status": "启动成功"}), 200
        else:
            return jsonify({"error": "启动失败"}), 502
    except Exception as e:
        log.logger.error(str(e))
        return jsonify({"error": "内部错误"}), 500

# program
@app.route('/program', methods=['GET'])
def program_api_root():
    return '<h1>Welcome to PCSMT2 Program API!</h1>'

@app.route('/program/version', methods=['GET'])
def program_version_api():
    try:
        return jsonify(program_info.PCSMTVersion + '-' + program_info.config['Release_Version'])
    except Exception as e:
        # 记录错误日志（建议使用 logging 模块）
        # 返回 JSON 格式的错误信息和 500 状态码
        log.logger.error('获取程序信息时发生内部错误')
        return jsonify({"error": "获取程序信息时发生内部错误"}), 500


def run_flask():
    app.run(port=5000)