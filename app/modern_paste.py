from flask import Flask
import flask_login
import flask_sqlalchemy

app = Flask(__name__)
app.config.from_object('flask_config')
db = flask_sqlalchemy.SQLAlchemy(app, session_options={
    'expire_on_commit': False,
})
session = db.session

login_manager = flask_login.LoginManager()
login_manager.init_app(app)


import models
from views import *


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=config.BUILD_ENVIRONMENT == constants.build_environment.DEV)
