from flask import redirect
from flask.ext.login import logout_user

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
    return 'user/login.html', {}


@app.route(UserRegisterInterfaceURI.path, methods=['GET'])
@hide_if_logged_in(redirect_uri=HomeURI.uri())
@render_view
def user_register_interface():
    return 'user/register.html', {}


@app.route(UserAccountInterfaceURI.path, methods=['GET'])
@require_login_frontend
@render_view
def user_account_interface():
    return 'user/account.html', {}


@app.route(UserLogoutInterfaceURI.path, methods=['GET'])
def user_logout_interface():
    logout_user()
    return redirect(HomeURI.uri())
