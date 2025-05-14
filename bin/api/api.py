import bin.api.main as main

@main.app.route('/api', methods=['GET'])
def api_root():
    return '<h1>Welcome to PCSMT2 API!</h1>'