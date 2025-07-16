import bin.api.main as main
from flask import jsonify
from bin.export import Info
from bin.export import log

# program
@main.app.route('/api/program', methods=['GET'])
def program_api_root():
    return '<h1>Welcome to PCSMT2 Program API!</h1>'

@main.app.route('/api/program/version', methods=['GET'])
def program_version_api():
    try:
        return jsonify(
            {
                'version': Info.Config.PCSMT2_Version() + '-' + Info.Config.Config['ReleaseVersion']
            }
        )
    except Exception as e:
        # 记录错误日志（建议使用 logging 模块）
        # 返回 JSON 格式的错误信息和 500 状态码
        log.logger.error('获取程序信息时发生内部错误')
        return jsonify({"error": "获取程序信息时发生内部错误"}), 500

@main.app.route('/api/program/minecraft_version', methods=['GET'])
def MinecraftVersion():
    try:
        return jsonify(
            {
                'minecraft_version': Info.Information.MinecraftVersion
            }
        )
    except Exception as e:
        # 记录错误日志（建议使用 logging 模块）
        # 返回 JSON 格式的错误信息和 500 状态码
        log.logger.error('获取Minecraft版本时发生内部错误')
        log.logger.error(e)
        return jsonify({"error": "获取Minecraft版本时发生内部错误"}), 500