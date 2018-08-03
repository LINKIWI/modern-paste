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

def setup_oidc():
    from flask_oidc import OpenIDConnect
    from api.authentication import oidc_request_loader
    app.config['OIDC_CLIENT_SECRETS'] = config.AUTH_OIDC_CLIENT_SECRETS
    oidc = OpenIDConnect(app)
    app.before_request(oidc_request_loader)

if config.AUTH_METHOD == 'oidc':
    setup_oidc()


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=config.BUILD_ENVIRONMENT == constants.build_environment.DEV)
