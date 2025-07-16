import bin.api.main as main
import json
from flask import jsonify, send_file
from bin.export import Info
from bin.export import log
from bin.find_files import find_file
from bin.command import Server
from bin.export import Admin
from flask import session, redirect, url_for
from flask import render_template
from flask import request
from bin.export import Get
from bin.export import RCON
from bin.export import Examine
from bin.download import Download
from urllib.parse import urlparse, urljoin
import time
import os

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
                "serverlist": Info.Information.ServerList,
                "serverCount": str(len(Info.Information.ServerList))
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
        server_info = Server.Get.Search(server_name, True)
        if server_info == False:
            log.logger.error('服务器不存在')
            return jsonify({"error": "服务器不存在"}), 404
        else:
            return jsonify({
                'version': server_info['Version'],
                'size': server_info['Size'],
                'startCount': server_info['Counts'],
                'LatestStartedTime': server_info['LatestStartedTime']
            }), 200
    except Exception as e:
        # 记录错误日志（建议使用 logging 模块）
        # 返回 JSON 格式的错误信息和 500 状态码
        log.logger.error('获取服务器信息时发生内部错误')
        return jsonify({"error": "获取服务器信息时发生内部错误"}), 500

@main.app.route('/api/server/latest', methods=['GET'])
def start_latest_server():
    try:
        server_lists = find_file.find_files_with_existence(Info.work_path + Info.File.Folder.Resource + Info.File.Document.Latest_json)
        if server_lists == False:
            log.logger.error('未找到服务器，请检查服务器名称是否正确！')
            return False
        else:
            with open(Info.work_path + Info.File.Folder.Resource + Info.File.Document.Latest_json, 'r', encoding='utf-8') as f:
                server_info = json.load(f)
                f.close()
            if not 'LastStartTime' in server_info:
                server_info['LastStartTime'] = 'N/A'
        return jsonify(
            {
                'name': server_info['Name'],
                'version': server_info['Version'],
                'size': server_info['Size'],
                'startCount': server_info['Counts'],
                'LatestStartedTime': server_info['LatestStartedTime']
            }
        )
    except Exception as e:
        # 记录错误日志（建议使用 logging 模块）
        # 返回 JSON 格式的错误信息和 500 状态码
        log.logger.error('启动服务器时发生内部错误')
        return jsonify({"error": "启动服务器时发生内部错误"}), 500

def admin_required(f):
    def wrapper(*args, **kwargs):
        if 'authenticated' not in session:
            # 判断是否为AJAX请求
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # 返回401错误，让前端处理跳转
                return jsonify({"error": "Unauthorized"}), 401
            else:
                session['next_url'] = request.url
                return redirect(url_for('login'))  # 非AJAX请求仍重定向
        return f(*args, **kwargs)
    return wrapper


def is_safe_url(target):
    """
    验证重定向URL是否安全（防止开放重定向攻击）
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
            ref_url.netloc == test_url.netloc

@main.app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        account = request.form.get('admin_account')
        password = request.form.get('admin_password')

        if Admin.Examine.Password(account, password):
            session['authenticated'] = True  # 此处依赖secret_key
            next_url = session.pop('next_url', None)

            # 如果存在有效重定向目标，则跳转
            if next_url and is_safe_url(next_url):
                return redirect(next_url)
            return render_template('index.html')
        else:
            return render_template('login.html', error="账号或密码错误")
    return render_template('login.html')


@main.app.route('/api/server/<string:server_name>/start', methods=['GET', 'POST'])
@admin_required  # 认证装饰器
def start_server(server_name):
    try:
        success = Server.Do.Start(server_name)
        if success:
            return jsonify({"status": "starting"}), 200
        else:
            return jsonify({"error": "error"}), 502
    except Exception as e:
        log.logger.error(str(e))
        return jsonify({"error": "内部错误"}), 500

@main.app.route('/api/server/<string:server_name>/stop', methods=['GET', 'POST'], endpoint='stop_server')
@admin_required
def StopServer(server_name):
    """
    停止服务器
    :param server_name: 停止服务器名称
    """
    try:
        success = Server.Do.Stop(server_name)
        if success == True:
            return jsonify({"status": "stopped"}), 200
        else:
            return jsonify({"error": "error"}), 502
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
        server_storage_size = Get.Info.StorageSize(server_name)

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

@main.app.route('/api/server/status/<string:server_name>', methods=['GET'])
def ServerStatus(server_name):
    """
    获取服务器状态
    server_name: 服务器名称

    返回：
    {
        "status": "running" | "stopped",
        "message": "服务器已启动" | "服务器已停止"
    }
    """
    try:
        ServerInfo = Examine.Server.InfoKeys(server_name)
        status = RCON.Infomation.ServerStatus(ServerInfo)
        if status:
            return jsonify({"status": "starting", "message": "服务器已启动"}), 200
        else:
            return jsonify({"status": "stopped", "message": "服务器未启动"}), 502
    except Exception as e:
        log.logger.error('获取服务器状态时发生内部错误')
        log.logger.error(e)
        return jsonify({"error": "内部错误"}), 500

@main.app.route('/api/server/info/<string:server_name>/excel', methods=['POST'])
def server_excel(server_name):
    """
    生成指定服务器信息Excel文件
    server_name: 服务器名称
    """
    try:
        ServerInfo = Examine.Server.InfoKeys(server_name)
        multi_sheet = Download.Excel.SignalSheet(server_name, ServerInfo)
        multi_sheet.GenerateFile()
        multi_sheet.WriteData()
        # 返回文件路径
        file_path = multi_sheet.FilePath()

        return send_file(file_path, as_attachment=True)
    except Exception as e:
        log.logger.error('生成服务器信息Excel文件时发生错误')
        log.logger.error(e)
        return jsonify({"error": "生成文件失败"}), 500

@main.app.route('/api/server/list/excel', methods=['POST'])
def GetServerListExcel():
    """
    生成所有服务器信息Excel文件
    server_name: 服务器名称
    """
    try:
        server_list = Server.Get.List(ShowMessage=False)
        multi_sheet = Download.Excel.MultiSheet(server_list)
        multi_sheet.GenerateFile()
        multi_sheet.WriteData()
        # 返回文件路径
        file_path = multi_sheet.FilePath()

        return send_file(file_path, as_attachment=True)
    except Exception as e:
        log.logger.error('生成所有服务器信息Excel文件时发生错误')
        log.logger.error(e)
        return jsonify({"error": "生成文件失败"}), 500