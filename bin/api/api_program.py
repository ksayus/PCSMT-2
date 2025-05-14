import bin.api.main as main
from flask import jsonify
from bin.export import program_info
from bin.export import log

# program
@main.app.route('/api/program', methods=['GET'])
def program_api_root():
    return '<h1>Welcome to PCSMT2 Program API!</h1>'

@main.app.route('/api/program/version', methods=['GET'])
def program_version_api():
    try:
        return jsonify(program_info.PCSMTVersion + '-' + program_info.config['Release_Version'])
    except Exception as e:
        # 记录错误日志（建议使用 logging 模块）
        # 返回 JSON 格式的错误信息和 500 状态码
        log.logger.error('获取程序信息时发生内部错误')
        return jsonify({"error": "获取程序信息时发生内部错误"}), 500