<<<<<<< HEAD
import bin.api.main as main
from flask import jsonify, request, redirect, url_for
from bin.export import Info
from bin.export import log
from bin.export import Get
from bin.command import Program
from bin.api.api_server import admin_required
import json
import threading

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

@main.app.route('/api/program/clear_cache', methods=['POST'], endpoint='clear_cache')
@admin_required
def clear_cache():
    """清理缓存（删除历史日志与最近启动记录）"""
    try:
        Program.Format.Log()
        Program.Format.Latest()
        return jsonify({"success": True, "message": "缓存清理完成"})
    except Exception as e:
        log.logger.error('清理缓存时发生内部错误')
        log.logger.error(e)
        return jsonify({"error": "清理缓存时发生内部错误", "success": False}), 500

@main.app.route('/api/program/reset_settings', methods=['POST'], endpoint='reset_settings')
@admin_required
def reset_settings():
    """重置程序设置为默认值"""
    try:
        Program.Format.Settings()
        return jsonify({"success": True, "message": "设置已重置为默认值，重启程序后完全生效"})
    except Exception as e:
        log.logger.error('重置设置时发生内部错误')
        log.logger.error(e)
        return jsonify({"error": "重置设置时发生内部错误", "success": False}), 500

@main.app.route('/api/program/format_program', methods=['POST'], endpoint='format_program')
@admin_required
def format_program():
    """格式化程序（清理日志、缓存与设置）"""
    try:
        Program.Format.Log()
        Program.Format.Server()
        Program.Format.Latest()
        Program.Format.Settings()
        return jsonify({"success": True, "message": "程序格式化完成，建议重启程序"})
    except Exception as e:
        log.logger.error('格式化程序时发生内部错误')
        log.logger.error(e)
        return jsonify({"error": "格式化程序时发生内部错误", "success": False}), 500

@main.app.route('/api/program/check_update', methods=['POST'], endpoint='check_update')
@admin_required
def check_update():
    """检查程序更新（根据配置的更新源，后台执行）"""
    try:
        from bin.download import Update

        source = Info.Config.AutoUpdateSource()

        def _check():
            try:
                if source == 'Gitee':
                    Update.Source.Gitee()
                else:
                    Update.Source.Github()
            except Exception as e:
                log.logger.error('检查更新失败！')
                log.logger.error(e)

        threading.Thread(target=_check, daemon=True).start()
        return jsonify({"success": True, "message": f"正在通过 {source} 检查更新，结果请查看程序日志"})
    except Exception as e:
        log.logger.error('检查更新时发生内部错误')
        log.logger.error(e)
        return jsonify({"error": "检查更新时发生内部错误", "success": False}), 500
=======
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
>>>>>>> 95e86289eb46f54ed8b7cff04029780dc0b25b16
