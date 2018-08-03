from flask import redirect
from flask_login import logout_user

import config

from api.decorators import hide_if_logged_in
from api.decorators import require_login_frontend
from api.decorators import render_view
from modern_paste import app
from uri.main import *
from uri.user import *


@app.route(UserLoginInterfaceURI.path, methods=['GET'])
@hide_if_logged_in(redirect_uri=HomeURI.uri())
@render_view
def user_login_interface():
    auth_method = config.AUTH_METHOD
    if auth_method == 'oidc':
        from modern_paste import oidc
        return oidc.redirect_to_auth_server(HomeURI.uri())
    else:
        return 'user/login.html', {}


@app.route(UserRegisterInterfaceURI.path, methods=['GET'])
@hide_if_logged_in(redirect_uri=HomeURI.uri())
@render_view
def user_register_interface():
    if config.AUTH_METHOD != 'local':
        return redirect(HomeURI.uri())
    return 'user/register.html', {}


@app.route(UserAccountInterfaceURI.path, methods=['GET'])
@require_login_frontend()
@render_view
def user_account_interface():
    return 'user/account.html', {}


@app.route(UserLogoutInterfaceURI.path, methods=['GET'])
def user_logout_interface():
    logout_user()
    return redirect(HomeURI.uri())
