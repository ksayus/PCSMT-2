import bin.api.main as main
import json
from flask import jsonify, send_file
from bin.export import Info
from bin.export import log
from bin.find_files import find_file
from bin.command import Server
from bin.command import Program
from bin.export import Admin
from flask import session, redirect, url_for, request, render_template
from bin.export import Get
from bin.export import RCON
from bin.export import timer
from bin.export import Examine
from bin.download import Download
from urllib.parse import urlparse, urljoin
# server
@main.app.route('/api/server', methods=['GET'])
def server_api_root():
    return '<h1>Welcome to PCSMT2 Server API!</h1>'

@main.app.route('/api/server/list', methods=['GET'])
def server_lists():
    try:
        # 使用 jsonify 返回 JSON 格式的响应
        ServerList = Server.Get.List(ShowMessage=False)

        return jsonify(
            {
                "serverlist": ServerList,
                "serverCount": str(ServerList)
            }
        )
    except Exception as e:
        # 记录错误日志（建议使用 logging 模块）
        # 返回 JSON 格式的错误信息和 500 状态码
        log.logger.error('获取服务器列表时发生内部错误')
        return jsonify({"error": "获取服务器列表时发生内部错误"}), 500

@main.app.route('/api/server/players/<string:ServerName>', methods=['GET'])
def server_players(ServerName):
    try:
        # 获取数据并验证结构
        server_data = timer.Heartbeat_instance.GetList()
        if not server_data or 'Name' not in server_data or 'Online' not in server_data:
            log.logger.error(f'数据为空: {server_data}')
            return jsonify({"error": "数据为空"}), 500

        # 重构为更安全的处理逻辑
        found = False
        player_status = None

        for i in range(len(server_data['Name'])):
            if server_data['Name'][i] == ServerName:
                player_status = server_data['Online'][i]
                found = True
                break

        if not found:
            log.logger.error(f'未找到服务器: {ServerName}')
            return jsonify({"error": "服务器不存在"}), 404

        return jsonify({
            "server": ServerName,
            "players": player_status  # 根据实际数据结构调整
        })
    except Exception as e:
        log.logger.error(f'获取玩家列表错误: {str(e)}')
        return jsonify({"error": "内部服务器错误"}), 500

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
            return redirect('/')  # 确保始终重定向到安全路径
        else:
            return render_template('login.html', error="账号或密码错误")
    return render_template('login.html')


@main.app.route('/api/server/<string:server_name>/start', methods=['GET', 'POST'], endpoint='start_server')
@admin_required
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
    :param server_name: 服务器名称

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
    :param server_name: 服务器名称
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

    :param server_name: 服务器名称
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

@main.app.route('/api/server/delete/<string:server_name>', methods=['POST'], endpoint='delete_server')
@admin_required
def DeleteServer(server_name):
    """
    删除服务器

    :param server_name: 删除服务器名称
    """
    try:
        log.Debug(f'删除服务器: {server_name}')
        success = Server.Processing.Delete(server_name, False)

        if success:
            return jsonify({"status": "deleted"}), 200
        else:
            return jsonify({"error": "删除错误"}), 502
    except Exception as e:
        log.logger.error(str(e))
        return jsonify({"error": "内部错误"}), 500

@main.app.route('/api/server/get/document/server.properties/<string:server_name>', methods=['GET'])
def server_properties_document(server_name):
    try:
        properties_dict = {}
        for item in Server.Get.Properties(server_name):
            # 确保配置项是键值对格式
            if isinstance(item, (tuple, list)) and len(item) == 2:
                key, value = item
                properties_dict[key] = value
            else:
                log.logger.warning(f"Invalid property format: {item}")

        return jsonify(properties_dict), 200
    except Exception as e:
        log.logger.error(str(e))
        return jsonify({"error": "内部错误"}), 500

@main.app.route('/api/server/get/run_memory/<string:server_name>', methods=['GET'])
def get_run_memory(server_name):
    try:
        RunMemory = Server.Get.RunMemory(server_name)
        return jsonify(
            {
                "min": RunMemory['Xms'],
                "max": RunMemory['Xmx']
            }
        )
    except Exception as e:
        log.logger.error(str(e))
        return jsonify({"error": "内部错误"}), 500

@main.app.route('/api/server/set/settings/<string:server_name>', methods=['POST'])
def set_server_settings(server_name):
    try:
        # 获取请求数据
        request_data = request.form

        # 获取参数
        new_name = request_data.get('serverName', type=str)
        port = request_data.get('server-port', type=int)
        min_memory = request_data.get('min-memory', type=int)
        max_memory = request_data.get('max-memory', type=int)
        gamemode = request_data.get('gamemode', type=str)
        difficulty = request_data.get('difficulty', type=str)
        max_players = request_data.get('max-players', type=int)
        max_world_size = request_data.get('max-world-size', type=int)
        spawn_protection = request_data.get('spawn-protection', type=int)
        # 安全转换布尔值属性
        spawn_monsters = 'true' if request_data.get('spawn-monsters') == 'on' else 'false'
        pvp = 'true' if request_data.get('pvp') == 'on' else 'false'
        allow_flight = 'true' if request_data.get('allow-flight') == 'on' else 'false'
        enable_command_block = 'true' if request_data.get('enable-command-block') == 'on' else 'false'
        white_list = 'true' if request_data.get('white-list') == 'on' else 'false'
        online_mode = 'true' if request_data.get('online-mode') == 'on' else 'false'
        hardcore = 'true' if request_data.get('hardcore') == 'on' else 'false'

        # 修改配置文件
        Server.Change.Properties(server_name, 'server-port', str(port))
        Server.Change.Properties(server_name, 'gamemode', str(gamemode))
        Server.Change.Properties(server_name, 'difficulty', str(difficulty))
        Server.Change.Properties(server_name, 'max-players', str(max_players))
        Server.Change.Properties(server_name, 'max-world-size', str(max_world_size))
        Server.Change.Properties(server_name, 'spawn-protection', str(spawn_protection))
        Server.Change.Properties(server_name, 'spawn-monsters', spawn_monsters)
        Server.Change.Properties(server_name, 'pvp', pvp)
        Server.Change.Properties(server_name, 'allow-flight', allow_flight)
        Server.Change.Properties(server_name, 'enable-command-block', enable_command_block)
        Server.Change.Properties(server_name, 'white-list', white_list)
        Server.Change.Properties(server_name, 'online-mode', online_mode)
        Server.Change.Properties(server_name, 'hardcore', hardcore)
        # 修改服务器运行内存
        Server.Change.RunningMemories(server_name, min_memory, max_memory)
        # 重命名服务器
        Server.Change.Rename(server_name, new_name)
        return jsonify({"message": "修改成功"}), 200
    except Exception as e:
        log.logger.error(str(e))
        return jsonify({"error": "内部错误"}), 500

@main.app.route('/api/server/get/<server_name>/terminal/logs', methods=['GET'])
def get_server_terminal_logs(server_name):
    """
    获取服务器控制台日志
    """
    try:
        Server.Get.TerminalLogs(server_name)
    except Exception as e:
        log.logger.error(e)
        return False

@admin_required
@main.app.route('/api/server/<string:server_name>/command', methods=['POST'])
def execute_server_command(server_name):
    """
    执行服务器命令
    """
    try:
        ServerInfo = Examine.Server.InfoKeys(server_name)

        response = request.get_json()
        log.logger.debug(response)

        result = RCON.Do.Command(ServerInfo, response['command'])

        if result == False:
            return jsonify({'success': False, 'message': '服务器未启动'})
        else:
            return jsonify({'success': True, 'message': result})
    except Exception as e:
        log.logger.error(str(e))
        return jsonify({"error": "内部错误"}), 500

@main.app.route('/api/server/get/banned/players/<string:server_name>')
def get_banned_players(server_name):
    """
    获取封禁玩家列表

    :param server_name: 服务器名称
    :return: 封禁玩家列表
    """
    try:
        server_info = Examine.Server.InfoKeys(server_name)

        BannedPlayerList = Server.Get.BannedPlayers(server_info)

        return jsonify(
            {
                "success": True,
                "message": "获取封禁玩家列表成功",
                "BannedPlayerList": BannedPlayerList
            }
        )
    except Exception as e:
        log.logger.error(str(e))
        return jsonify({"error": "获取封禁玩家列表时发生内部错误", "success": False})

@main.app.route('/api/server/get/white-list/<string:server_name>')
def get_white_list(server_name):
    """
    获取白名单列表

    :param server_name: 服务器名称
    :return: 白名单列表
    """
    try:
        server_info = Examine.Server.InfoKeys(server_name)

        WhiteList = Server.Get.WhiteList(server_info)

        if WhiteList == False:
            return jsonify(
                {
                    "success": False,
                    "message": "白名单未启用"
                }
            )
        else:
            return jsonify(
                {
                    "success": True,
                    "message": "获取白名单列表成功",
                    "WhiteList": WhiteList
                }
            )
    except Exception as e:
        log.logger.error(str(e))
        return jsonify({"error": "获取白名单列表时发生内部错误", "success": False})

@main.app.route('/api/server/get/history/players/<string:server_name>')
def get_history_players(server_name):
    """
    获取历史玩家列表

    :param server_name: 服务器名称
    :return: 历史玩家列表
    """
    try:
        server_info = Examine.Server.InfoKeys(server_name)

        HistoryPlayerList = Server.Get.HistoryPlayers(server_info)

        if len(HistoryPlayerList) == 0:
            return jsonify(
                {
                    "success": False,
                    "message": "无历史玩家"
                }
            )
        else:
            return jsonify(
                {
                    "success": True,
                    "message": "获取历史玩家列表成功",
                    "HistoryPlayerList": HistoryPlayerList
                }
            )
    except Exception as e:
        log.logger.error(str(e))
        return jsonify({"error": "获取历史玩家列表时发生内部错误", "success": False})

@main.app.route('/api/program/get/CPU/Usage')
def get_CPU_Usage():
    """获取CPU占用率"""
    try:
        # 获取CPU占用率
        CPU_Usage_Percent, CPU_Freq_now, CPU_Freq_Max = Program.Get.CPU_Usage()

        return jsonify(
            {
                "success": True,
                "message": "获取CPU占用率成功",
                "used": CPU_Usage_Percent,
                "total": CPU_Freq_Max,
                "abs_used": round(CPU_Freq_now, 2),
                "abs_total": round(CPU_Freq_Max, 2)
            }
        )
    except Exception as e:
        log.logger.error('获取CPU占用率失败！')
        log.logger.error(e)
        return

@main.app.route('/api/program/get/RAM/Usage')
def get_RAM_Usage():
    """获取RAM占用率"""
    try:
        # 获取RAM占用率
        RAM_Usage_Percent, RAM_Usage_MB = Program.Get.RAM_Usage()
        return jsonify(
            {
                "success": True,
                "message": "获取RAM占用率成功",
                "used": RAM_Usage_Percent,
                "total": RAM_Usage_MB,
                "abs_used": round(RAM_Usage_MB, 2),
                "abs_total": round(RAM_Usage_MB / (RAM_Usage_Percent / 100), 2)
            }
        )
    except Exception as e:
        log.logger.error('获取RAM占用率失败！')
        log.logger.error(e)
        return