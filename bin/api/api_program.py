import bin.api.main as main
from flask import jsonify, request, redirect, url_for
from bin.export import Info
from bin.export import log
from bin.export import Get
from bin.command import Program
import json

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

@main.app.route('/api/program/disk_usage', methods=['GET'])
def disk_usage():
    try:
        DiskUsage, DiskFree, Usage, Free = Get.Info.DiskUsage()
        return jsonify({
            "disk_usage": DiskUsage,
            "disk_free": DiskFree,
            "usage": Usage,
            "free": Free
        })
    except Exception as e:
        # 返回 JSON 格式的错误信息和 500 状态码
        log.logger.error('获取磁盘使用情况时发生内部错误')
        log.logger.error(e)
        return jsonify({"error": "获取磁盘使用情况时发生内部错误"}), 500

@main.app.route('/api/program/get/settings', methods=['GET'])
def get_settings():
    try:
        # 获取配置文件
        with open(('./config.json'), 'r', encoding='utf-8') as f:
            config = json.load(f)

        settings = {
            'min_memory': config['RunningMemories_Min'],
            'max_memory': config['RunningMemories_Max'],
            'nogui_enabled': config['Nogui'],
            'eula_wait_time': config['WaitEulaGenerateTime'],
            'auto_start': config['AutomaticStartup'],
            'update_source': config['AutoUpdateSource'],
            'test_versions': config['MinecraftTestVersion'],
            'storage_update_time': config['StorageSizeUpdateTime'],
            'server_port': config['Port']
        }

        return jsonify(settings)
    except Exception as e:
        # 返回 JSON 格式的错误信息和 500 状态码
        log.logger.error('获取设置时发生内部错误')
        log.logger.error(e)
        return jsonify({"error": "获取设置时发生内部错误"}), 500

@main.app.route('/api/program/set/settings', methods=['POST'])
def set_settings():
    try:
        log.Debug(request.data)  # 调试输出，确保表单数据正确
        data = request.get_json()
        log.Debug(data)  # 调试输出，确保数据正确
        config_data = {
            'memories_min': int(data['min_memory']),
            'memories_max': int(data['max_memory']),
            'nogui_enabled': bool(data['nogui_enabled']),
            'eula_wait_time': int(data['eula_wait_time']),
            'auto_start': bool(data['auto_start']),
            'update_source': str(data['update_source']),
            'test_versions': bool(data['test_versions']),
            'storage_update_time': int(data['storage_update_time']),
            'server_port': int(data['server_port']),
        }

        log.Debug(config_data)  # 调试输出，确保数据正确

        # 更新配置文件
        Program.Change.RunningMemories_Config(config_data['memories_min'], config_data['memories_max'])
        Program.Change.Nogui(config_data['nogui_enabled'])
        Program.Change.WaitEulaGenerateTime(config_data['eula_wait_time'])
        Program.Change.AutoStartup(config_data['auto_start'])
        Program.Change.UpdateSource(config_data['update_source'])
        Program.Change.MinecraftTestVersion(config_data['test_versions'])
        Program.Change.StorageSizeUpdateTime(config_data['storage_update_time'])
        Program.Change.Port(config_data['server_port'])

        # 改为返回JSON响应
        return jsonify({"success": True})
    except Exception as e:
        # 返回 JSON 格式的错误信息和 500 状态码
        log.logger.error('更新设置时发生内部错误')
        log.logger.error(e)
        return jsonify({"error": "更新设置时发生内部错误"}), 500