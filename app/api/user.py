from uri.user import *

import flask
from modern_paste import app

import config
import constants.api
import database.user
from flask_login import current_user
from flask_login import login_user
from api.decorators import require_form_args
from api.decorators import require_login_api
from api.decorators import require_local_auth
from util.exception import *


@app.route(UserCreateURI.path, methods=['POST'])
@require_local_auth
@require_form_args(['username', 'password'])
def create_new_user():
    """
    API endpoint for creating a new user.
    """
    if not config.ENABLE_USER_REGISTRATION:
        return (
            flask.jsonify(constants.api.USER_REGISTRATION_DISABLED_FAILURE),
            constants.api.USER_REGISTRATION_DISABLED_FAILURE_CODE,
        )

    data = flask.request.get_json()
    try:
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


@app.route(UserUpdateDetailsURI.path, methods=['POST'])
@require_local_auth
@require_login_api
def update_user_details():
    """
    Update the user profile of the currently logged-in user.
    """
    data = {
        field: value
        for field, value in flask.request.get_json().items()
        if value
    }
    try:
        if data.get('new_password') and (not data.get('current_password') or not database.user.authenticate_user(current_user.username, data.get('current_password'))):
            return flask.jsonify({
                constants.api.RESULT: constants.api.RESULT_FAULURE,
                constants.api.MESSAGE: 'Attempting to change user password and either current password was not '
                                       'supplied or is incorrect',
                constants.api.FAILURE: 'auth_failure',
            }), constants.api.AUTH_FAILURE_CODE
        new_user = database.user.update_user_details(
            user_id=current_user.user_id,
            name=data.get('name'),
            email=data.get('email'),
            new_password=data.get('new_password'),
        )
        return flask.jsonify({
            constants.api.RESULT: constants.api.RESULT_SUCCESS,
            constants.api.MESSAGE: None,
            'name': new_user.name,
            'email': new_user.email,
        }), constants.api.SUCCESS_CODE
    except InvalidEmailException:
        return flask.jsonify({
            constants.api.RESULT: constants.api.RESULT_FAULURE,
            constants.api.MESSAGE: 'Email address {email_addr} is invalid'.format(email_addr=data.get('email')),
            constants.api.FAILURE: 'invalid_email_failure',
        }), constants.api.INCOMPLETE_PARAMS_FAILURE_CODE
    except:
        return flask.jsonify(constants.api.UNDEFINED_FAILURE), constants.api.UNDEFINED_FAILURE_CODE


@app.route(UserDeactivateURI.path, methods=['POST'])
@require_local_auth
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
@require_local_auth
@require_login_api
def api_key_regenerate():
    """
    Generate a new API key for the currently logged-in user.
    """
    try:
        return flask.jsonify({
            constants.api.RESULT: constants.api.RESULT_SUCCESS,
            constants.api.MESSAGE: None,
            'api_key': database.user.generate_new_api_key(current_user.user_id).api_key,
        }), constants.api.SUCCESS_CODE
    except:
        return flask.jsonify(constants.api.UNDEFINED_FAILURE), constants.api.UNDEFINED_FAILURE_CODE


@app.route(CheckUsernameAvailabilityURI.path, methods=['POST'])
@require_local_auth
@require_form_args(['username'])
def check_username_availability():
    """
    Check if the specified username is available for registration.
    """
    data = flask.request.get_json()
    try:
        return flask.jsonify({
            'username': data['username'],
            'is_available': database.user.is_username_available(data['username']),
        }), constants.api.SUCCESS_CODE
    except:
        return flask.jsonify(constants.api.UNDEFINED_FAILURE), constants.api.UNDEFINED_FAILURE_CODE


@app.route(ValidateEmailAddressURI.path, methods=['POST'])
@require_local_auth
@require_form_args(['email'])
def validate_email_address():
    """
    Check if the provided email address is valid.
    """
    data = flask.request.get_json()
    try:
        return flask.jsonify({
            'email': data['email'],
            'is_valid': database.user.is_email_address_valid(data['email']),
        }), constants.api.SUCCESS_CODE
    except:
        return flask.jsonify(constants.api.UNDEFINED_FAILURE), constants.api.UNDEFINED_FAILURE_CODE
