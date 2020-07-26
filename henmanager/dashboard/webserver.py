from flask import render_template
from flask import Flask
from flask import request

dashboard = Flask(__name__)

@dashboard.route('/')
@dashboard.route('/index')
def index():
    user = {'username': 'Touillet'}
    if request.method == 'POST':
        if request.form['test_button'] == "Test":
            print("Hooray!")
    return render_template('index.html', title='Dashboard', hatch='Open', user=user)

if __name__ == "__main__":
    dashboard.run(debug=True, port=80, host='192.168.1.44')
