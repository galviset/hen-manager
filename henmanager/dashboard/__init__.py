from flask import Flask

dashboard = Flask(__name__)

from henmanager.dashboard import routes