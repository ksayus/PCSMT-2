import bin.api.main as main
from flask import render_template
from flask import request
from bin.command import Server
import time

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

@main.app.route('/server/<string:server_name>/storage_chart')
def server_storage_chart(server_name):
    """渲染存储图表页面"""
    return render_template('chart_js.html', server_name=server_name)