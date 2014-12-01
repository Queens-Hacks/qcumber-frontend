from flask import Flask

APP = Flask(__name__)
APP.config.from_object('qcumber.default_config')

from qcumber import views
