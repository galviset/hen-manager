from flask import render_template
from flask import Flask

dashboard = Flask(__name__)

@dashboard.route('/')
@dashboard.route('/index')
def index():
    user = {'username': 'Touillet'}
    return render_template('index.html', title='Dashboard', hatch='Open', user=user)

if __name__ == "__main__":
    dashboard.run(debug=True, port=80, host='192.168.1.44')
