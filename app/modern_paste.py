from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

app = Flask(__name__)
app.config.from_object('flask_config')
db = SQLAlchemy(app, session_options={
    'expire_on_commit': False,
})
session = db.session

login_manager = LoginManager()
login_manager.init_app(app)


import models
from views import *


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=config.BUILD_ENVIRONMENT == constants.build_environment.DEV)
