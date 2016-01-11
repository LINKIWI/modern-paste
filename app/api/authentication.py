import flask
from flask import request
from flask.ext.login import current_user
from flask.ext.login import login_required
from flask.ext.login import login_user as login
from flask.ext.login import logout_user as logout

import constants.api
import database.user
from api.decorators import require_form_args
from modern_paste import app
from uri.authentication import *
from util.exception import *


@app.route(LoginUserURI.path, methods=['POST'])
@require_form_args(['username', 'password'])
def login_user():
    """
    Authenticate and log in a user.
    """
    data = request.get_json()
    success_resp = flask.jsonify({
        constants.api.RESULT: constants.api.RESULT_SUCCESS,
        constants.api.MESSAGE: None,
        'username': data['username'],
    }), constants.api.SUCCESS_CODE

    if current_user.is_authenticated:
        # Already logged in; no action is required
        return success_resp

    try:
        if not database.user.authenticate_user(data['username'], data['password']):
            return flask.jsonify(constants.api.AUTH_FAILURE), constants.api.AUTH_FAILURE_CODE
    except UserDoesNotExistException:
        return flask.jsonify(constants.api.NONEXISTENT_USER_FAILURE), constants.api.NONEXISTENT_USER_FAILURE_CODE

    login(
        user=database.user.get_user_by_username(data['username']),
        remember=bool(data.get('remember_me', False)),
    )
    return success_resp


@app.route(LogoutUserURI.path, methods=['POST'])
@login_required
def logout_user():
    """
    Log the current user out, as applicable.
    """
    username = str(current_user.username)
    logout()
    return flask.jsonify({
        constants.api.RESULT: constants.api.RESULT_SUCCESS,
        constants.api.MESSAGE: None,
        'username': username,
    }), constants.api.SUCCESS_CODE


@app.route(AuthStatusURI.path, methods=['POST'])
def auth_status():
    """
    Gets the authentication status for the current user, if any.
    """
    return flask.jsonify({
        'is_authenticated': bool(current_user.is_authenticated),
        'user_details': {
            'username': getattr(current_user, 'username', None),
            'user_id': getattr(current_user, 'user_id', None),
        },
    }), constants.api.SUCCESS_CODE
