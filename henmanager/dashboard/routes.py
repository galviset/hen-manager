from henmanager.dashboard import dashboard

@dashboard.route('/')
@dashboard.route('/index')
def index():
    return "Hello World!"