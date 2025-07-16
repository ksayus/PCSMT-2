import bin.api.main as main
from flask import render_template
from flask import request
from bin.command import Server
import time

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

@main.app.route('/server/create', endpoint='server_create', methods=['GET', 'POST'])
def server_create():
    if request.method == 'POST':
        Name = request.form.get('serverName')
        CoreType = request.form.get('coreType')
        CoreVersion = request.form.get('coreVersion')
        Port = request.form.get('port')
        Enable_PVP = request.form.get('pvpEnabled')
        OnlineMode = request.form.get('onlineMode')
        GameMode = request.form.get('gameMode')

        Server.Processing.Build(Name, CoreType, CoreVersion)
        Server.Do.Start(Name)
        time.sleep(40)
        Server.Do.Stop(Name)
        time.sleep(3)
        Server.Change.Properties(Name, 'server-port', Port)
        Server.Change.Properties(Name, 'pvp', Enable_PVP)
        Server.Change.Properties(Name, 'online-mode', OnlineMode)
        Server.Change.Properties(Name, 'gamemode', GameMode)
        return render_template('index.html')


    return render_template('CreateServer.html')