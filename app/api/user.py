from uri.user import *

import flask
from modern_paste import app

import constants.api
import database.user
from flask.ext.login import current_user
from flask.ext.login import login_user
from api.decorators import require_form_args
from api.decorators import require_login_api
from util.exception import *


@app.route(UserCreateURI.path, methods=['POST'])
@require_form_args(['username', 'password'])
def create_new_user():
    """
    API endpoint for creating a new user.
    """
    try:
        data = flask.request.get_json()
        new_user = database.user.create_new_user(
            username=data['username'],
            password=data['password'],
            signup_ip=flask.request.remote_addr,
            name=data.get('name'),
            email=data.get('email'),
        )
        login_user(new_user)
        return flask.jsonify({
            constants.api.RESULT: constants.api.RESULT_SUCCESS,
            constants.api.MESSAGE: None,
            'username': new_user.username,
            'name': new_user.name,
            'email': new_user.email,
        }), constants.api.SUCCESS_CODE
    except UsernameNotAvailableException:
        return flask.jsonify({
            constants.api.RESULT: constants.api.RESULT_FAULURE,
            constants.api.MESSAGE: 'Username is not available',
            constants.api.FAILURE: 'username_not_available_failure',
        }), constants.api.INCOMPLETE_PARAMS_FAILURE_CODE
    except InvalidEmailException:
        return flask.jsonify({
            constants.api.RESULT: constants.api.RESULT_FAULURE,
            constants.api.MESSAGE: 'Email address {email_addr} is invalid'.format(email_addr=data.get('email')),
            constants.api.FAILURE: 'invalid_email_failure',
        }), constants.api.INCOMPLETE_PARAMS_FAILURE_CODE
    except:
        return flask.jsonify(constants.api.UNDEFINED_FAILURE), constants.api.UNDEFINED_FAILURE_CODE


@app.route(UserDeactivateURI.path, methods=['POST'])
@require_login_api
def deactivate_user():
    """
    Deactivate the currently logged-in user.
    """
    try:
        database.user.deactivate_user(current_user.user_id)
        return flask.jsonify({
            constants.api.RESULT: constants.api.RESULT_SUCCESS,
            constants.api.MESSAGE: None,
            'username': current_user.username,
        }), constants.api.SUCCESS_CODE
    except:
        return flask.jsonify(constants.api.UNDEFINED_FAILURE), constants.api.UNDEFINED_FAILURE_CODE


@app.route(UserAPIKeyRegenerateURI.path, methods=['POST'])
@require_login_api
def api_key_regenerate():
    try:
        return flask.jsonify({
            constants.api.RESULT: constants.api.RESULT_SUCCESS,
            constants.api.MESSAGE: None,
            'api_key': database.user.generate_new_api_key(current_user.user_id).api_key,
        }), constants.api.SUCCESS_CODE
    except:
        return flask.jsonify(constants.api.UNDEFINED_FAILURE), constants.api.UNDEFINED_FAILURE_CODE


@app.route(CheckUsernameAvailabilityURI.path, methods=['POST'])
@require_form_args(['username'])
def check_username_availability():
    """
    Check if the specified username is available for registration.
    """
    try:
        data = flask.request.get_json()
        return flask.jsonify({
            'username': data['username'],
            'is_available': database.user.is_username_available(data['username']),
        }), constants.api.SUCCESS_CODE
    except:
        return flask.jsonify(constants.api.UNDEFINED_FAILURE), constants.api.UNDEFINED_FAILURE_CODE


@app.route(ValidateEmailAddressURI.path, methods=['POST'])
@require_form_args(['email'])
def validate_email_address():
    """
    Check if the provided email address is valid.
    """
    try:
        data = flask.request.get_json()
        return flask.jsonify({
            'email': data['email'],
            'is_valid': database.user.is_email_address_valid(data['email']),
        }), constants.api.SUCCESS_CODE
    except:
        return flask.jsonify(constants.api.UNDEFINED_FAILURE), constants.api.UNDEFINED_FAILURE_CODE
