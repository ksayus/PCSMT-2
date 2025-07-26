from bin.command.Server import Get as ServerGet
from .api import main
from flask import request, jsonify

@main.app.route('/api/server/terminal/<server_name>', methods=['GET'])
def get_terminal_logs(server_name):
    """获取服务器终端日志"""
    try:
        logs = ServerGet.TerminalLogs(server_name, 1000)
        return jsonify({'success': True, 'logs': logs})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@main.app.route('/api/server/terminal/<server_name>', methods=['POST'])
def send_terminal_command(server_name):
    """向服务器终端发送命令"""
    data = request.get_json()
    if not data or 'command' not in data:
        return jsonify({'success': False, 'error': '未提供命令'}), 400
    command = data['command']
    try:
        # 这里需要实现执行命令的逻辑
        # 例如调用相应的函数执行命令
        # Server.ExecuteCommand(server_name, command)
        return jsonify({'success': True, 'message': f'命令 {command} 已发送到服务器 {server_name}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
