from henmanager.dashboard import dashboard
from flask import render_template

@dashboard.route('/')
@dashboard.route('/index')
def index():
    user = {'username': 'Luxen'}
    return render_template('index.html', title='Dashboard', hatch='Open', user=user)
