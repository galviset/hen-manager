from flask import Flask
from dashboard import routes

dashboard = Flask(__name__)
if __name__ == "__main__":
        dashboard.run(debug=True, port=80, host='192.168.1.44')
