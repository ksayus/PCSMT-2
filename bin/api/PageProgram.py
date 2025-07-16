import bin.api.main as main
from flask import render_template

@main.app.route('/program/version', endpoint="program_version")
def program_version():
    return render_template('ProgramVersion.html')