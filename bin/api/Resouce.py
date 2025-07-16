import bin.api.main as main
from flask import send_from_directory

@main.app.route('/api/static/ico', methods=['GET'], endpoint='APIStaticIco')
def api_static_ico():
    # 使用 send_from_directory 发送静态文件
    return send_from_directory('static', 'PCSMT2.ico')