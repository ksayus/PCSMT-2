<<<<<<< HEAD
import bin.api.main as main
from flask import send_from_directory

@main.app.route('/api/static/ico', methods=['GET'], endpoint='APIStaticIco')
def api_static_ico():
    # 使用 send_from_directory 发送静态文件
=======
import bin.api.main as main
from flask import send_from_directory

@main.app.route('/api/static/ico', methods=['GET'], endpoint='APIStaticIco')
def api_static_ico():
    # 使用 send_from_directory 发送静态文件
>>>>>>> 95e86289eb46f54ed8b7cff04029780dc0b25b16
    return send_from_directory('static', 'PCSMT2.ico')