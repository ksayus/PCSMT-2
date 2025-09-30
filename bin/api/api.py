import bin.api.main as main
from flask import render_template

@main.app.route('/', methods=['GET'])
def root():
    return render_template('index.html')

@main.app.route('/api', methods=['GET'])
def api_root():
    return '<h1>Welcome to PCSMT2 API!</h1>'