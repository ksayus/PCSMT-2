from flask import Flask, jsonify, request
from bin.command import server
from bin.export import program_info
from bin.export import log
from bin.find_files import find_file
import json
app = Flask(__name__)

@app.route('/', methods=['GET'])
def api_root():
    return 'Welcome to PCSMT2 API!'


# server
@app.route('/server', methods=['GET'])
def server_api_root():
    return 'Welcome to PCSMT2 Server API!'

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

# program
@app.route('/program', methods=['GET'])
def program_api_root():
    return 'Welcome to PCSMT2 Program API!'

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