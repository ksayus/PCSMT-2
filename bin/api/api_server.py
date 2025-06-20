import bin.api.main as main
import json
from flask import jsonify, request
from bin.export import program_info
from bin.export import log
from bin.find_files import find_file
from bin.command import server
from bin.export import admin
from flask import session, redirect, url_for
from flask import render_template
from flask import request
from bin.export import get

# server
@main.app.route('/api/server', methods=['GET'])
def server_api_root():
    return '<h1>Welcome to PCSMT2 Server API!</h1>'

@main.app.route('/api/server/list', methods=['GET'])
def server_lists():
    try:
        # 使用 jsonify 返回 JSON 格式的响应
        return jsonify(
            {
                "serverlist": program_info.server_list
            }
        )
    except Exception as e:
        # 记录错误日志（建议使用 logging 模块）
        # 返回 JSON 格式的错误信息和 500 状态码
        log.logger.error('获取服务器列表时发生内部错误')
        return jsonify({"error": "获取服务器列表时发生内部错误"}), 500

@main.app.route('/api/server/info/<string:server_name>', methods=['GET'])
def server_info(server_name):
    try:
        server_info = server.search_server(server_name)
        if server_info == False:
            log.logger.error('服务器不存在')
            return jsonify({"error": "服务器不存在"}), 404
        else:
            return jsonify({
                'version': server_info['server_version'],
                'size': server_info['server_size'],
                'startCount': server_info['start_count'],
            }), 200
    except Exception as e:
        # 记录错误日志（建议使用 logging 模块）
        # 返回 JSON 格式的错误信息和 500 状态码
        log.logger.error('获取服务器信息时发生内部错误')
        return jsonify({"error": "获取服务器信息时发生内部错误"}), 500

@main.app.route('/api/server/latest', methods=['GET'])
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
        return jsonify(
            {
                'name': server_info['server_name'],
                'version': server_info['server_version'],
                'size': server_info['server_size'],
                'startCount': server_info['start_count'],
            }
        )
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

@main.app.route('/login', methods=['GET', 'POST'])
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


@main.app.route('/api/server/<string:server_name>/start', methods=['GET'])
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

@main.app.route('/api/server/<string:server_name>/storage_chart')
def server_storage_chart(server_name):
    """渲染存储图表页面"""
    return render_template('chart_js.html', server_name=server_name)

@main.app.route('/api/server/<string:server_name>/storage_info', methods=['GET'])
def return_server_storage_info(server_name):
    """
    获取服务器存储信息
    :param server_name: 服务器名称
    """
    try:
        server_storage_size = get.get_server_storage_size(server_name)

        # 修改：提取数值部分并转换为浮点数
        numeric_values = []
        for val in server_storage_size['storage_size']:
            # 分离数值和单位（例如："5.2GB" -> 5.2）
            numeric_part = ''.join(c for c in val if c.isdigit() or c == '.')
            numeric_values.append(float(numeric_part))

        if server_storage_size['storage_size'][0] is None or server_storage_size['time'][0] is None:
            return jsonify({"error": "未找到信息"}), 400

        title = f'{server_name}服务器存储情况'

        types = ['TB', 'GB', 'MB', 'KB', 'B']
        now_type = 'B'  # 默认值，确保变量始终有值
        for this_type in types:
            if this_type in server_storage_size['storage_size'][0]:
                now_type = this_type
                break

        return jsonify({
            'title': title,
            'labels': server_storage_size['time'],
            'values': numeric_values,  # 使用转换后的数值数组
            'type': now_type
        }), 200
    except Exception as e:
        log.logger.error(str(e))
        return jsonify({"error": "内部错误"}), 500
