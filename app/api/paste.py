import flask
from flask_login import current_user
from modern_paste import app

from uri.paste import *
from util.exception import *
from api.decorators import require_form_args
import constants.api
import database.paste
import util.cryptography


@app.route(PasteSubmitURI.path, methods=['POST'])
@require_form_args(['contents'])
def submit_paste():
    """
    Endpoint for submitting a new paste.
    """
    data = flask.request.get_json()
    if data.get('user_id') and (not current_user.is_authenticated or current_user.user_id != data.get('user_id')):
        return flask.jsonify(constants.api.AUTH_FAILURE), constants.api.AUTH_FAILURE_CODE

    try:
        return flask.jsonify(database.paste.create_new_paste(**data).as_dict()), constants.api.SUCCESS_CODE
    except:
        return flask.jsonify(constants.api.UNDEFINED_FAILURE), constants.api.UNDEFINED_FAILURE_CODE


@app.route(PasteDeactivateURI.path, methods=['POST'])
@require_form_args(['paste_id'])
def deactivate_paste():
    """
    Endpoint for deactivating an existing paste.
    The user can deactivate a paste with this endpoint in two ways:
    (1) Supply a deactivation token in the request, or
    (2) Be currently logged in, and own the paste.
    """
    data = flask.request.get_json()
    try:
        paste = database.paste.get_paste_by_id(data['paste_id'])
        if (current_user.is_authenticated and current_user.user_id == paste.user_id) or data.get('deactivation_token') == paste.deactivation_token:
            database.paste.deactivate_paste(paste.paste_id)
            return flask.jsonify({
                constants.api.RESULT: constants.api.RESULT_SUCCESS,
                constants.api.MESSAGE: None,
                'paste_id': paste.paste_id,
            }), constants.api.SUCCESS_CODE
        fail_msg = 'User does not own requested paste' if current_user.is_authenticated else 'Deactivation token is invalid'
        return flask.jsonify({
            constants.api.RESULT: constants.api.RESULT_FAULURE,
            constants.api.MESSAGE: fail_msg,
            'paste_id': paste.paste_id,
        }), constants.api.AUTH_FAILURE_CODE
    except PasteDoesNotExistException:
        return flask.jsonify(constants.api.NONEXISTENT_PASTE_FAILURE), constants.api.NONEXISTENT_PASTE_FAILURE_CODE
    except:
        return flask.jsonify(constants.api.UNDEFINED_FAILURE), constants.api.UNDEFINED_FAILURE_CODE


@app.route(PasteDetailsURI.path, methods=['POST'])
@require_form_args(['paste_id'])
def paste_details():
    data = flask.request.get_json()
    try:
        paste = database.paste.get_paste_by_id(data['paste_id'])
        if not paste.password_hash or (data.get('password') and paste.password_hash == util.cryptography.secure_hash(data.get('password'))):
            return flask.jsonify({
                constants.api.RESULT: constants.api.RESULT_SUCCESS,
                constants.api.MESSAGE: None,
                'details': paste.as_dict(),
            }), constants.api.SUCCESS_CODE
        else:
            return flask.jsonify({
                constants.api.RESULT: constants.api.RESULT_FAULURE,
                constants.api.MESSAGE: 'Password-protected paste: either no password or wrong password supplied',
                'details': {},
            }), constants.api.AUTH_FAILURE_CODE
    except PasteDoesNotExistException:
        return flask.jsonify(constants.api.NONEXISTENT_PASTE_FAILURE), constants.api.NONEXISTENT_PASTE_FAILURE_CODE
    except:
        return flask.jsonify(constants.api.UNDEFINED_FAILURE), constants.api.UNDEFINED_FAILURE_CODE
