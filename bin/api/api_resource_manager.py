from bin.api import main
from bin.command.Manager import Manager
from bin.find_files.tree import Tree
from bin.command import Server
from bin.export import log
from flask import jsonify, render_template, request
import json
import os


@main.app.route('/manager/<string:server_name>', methods=['GET'])
def manager(server_name):
    try:
        server_info = Server.Get.Search(server_name)
        if server_info == False:
            return jsonify({"error": "服务器不存在"}), 404
        
        # 调试信息：检查服务器信息中的路径
        log.Debug(f'服务器信息路径: {server_info["Path"]}')
        log.Debug(f'服务器信息名称: {server_info["Name"]}')
        
        return render_template('manager.html', server_info=server_info)
    except Exception as e:
        # 记录错误日志（建议使用 logging 模块）
        # 返回 JSON 格式的错误信息和 500 状态码
        log.logger.error('获取服务器信息时发生内部错误')
        log.logger.error(e)
        return jsonify({"error": "获取服务器信息时发生内部错误"}), 500

@main.app.route('/api/get/directory', methods=['GET'])
def get_directory():
    try:
        # 从查询参数获取路径
        directory_path = request.args.get('path', '')

        if not directory_path:
            return jsonify({"error": "路径参数不能为空"}), 400

        # 防止路径穿越攻击
        directory_path = directory_path.replace('..', '')

        # 对 URL 编码的路径进行解码
        import urllib.parse
        directory_path = urllib.parse.unquote(directory_path)

        log.Debug(f'获取目录信息 (解码后): {directory_path}')

        # 检查路径是否存在
        if not os.path.exists(directory_path):
            return jsonify({"error": f"路径不存在: {directory_path}"}), 404

        # 创建 Tree 实例
        tree = Tree(directory_path)
        All_dire = tree.GetTree()
        Diretory = tree.CurrentTree()

        diretory_info = {
            'FilesCounts': len(All_dire),
            'CurrentDirectory': Diretory
        }
        return jsonify(diretory_info)
    except Exception as e:
        # 记录错误日志（建议使用 logging 模块）
        # 返回 JSON 格式的错误信息和 500 状态码
        log.logger.error('获取目录信息时发生内部错误')
        log.logger.error(e)
        return jsonify({"error": "获取目录信息时发生内部错误"}), 500