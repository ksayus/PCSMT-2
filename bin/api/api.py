<<<<<<< HEAD
import bin.api.main as main
from flask import render_template

@main.app.route('/', methods=['GET'])
def root():
    return render_template('index.html')

@main.app.route('/api', methods=['GET'])
def api_root():
=======
import bin.api.main as main
from flask import render_template

@main.app.route('/', methods=['GET'])
def root():
    return render_template('index.html')

@main.app.route('/api', methods=['GET'])
def api_root():
>>>>>>> 95e86289eb46f54ed8b7cff04029780dc0b25b16
    return '<h1>Welcome to PCSMT2 API!</h1>'