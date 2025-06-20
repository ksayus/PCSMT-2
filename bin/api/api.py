import bin.api.main as main
from flask import render_template

@main.app.route('/api', methods=['GET'])
def api_root():
    return '<h1>Welcome to PCSMT2 API!</h1>'

@main.app.route('/api/help', methods=['GET'])
def api_help():
    return render_template('help.html')