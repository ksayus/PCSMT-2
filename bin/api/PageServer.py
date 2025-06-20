import bin.api.main as main
from flask import render_template

# 添加唯一端点名避免路由冲突
@main.app.route('/server/info/<string:server_name>', endpoint='page_server_info_server_name')
def server_info(server_name):
    return render_template('ServerInfo.html', server_name=server_name)

@main.app.route('/server/latest', endpoint='page_server_latest')
def server_info_latest():
    return render_template('ServerLatest.html', server_name='latest')

@main.app.route('/server/list', endpoint='page_server_list')
def server_list():
    return render_template('ServerList.html')