import flask
from flask_login import current_user
from modern_paste import app

import config
from uri.main import *
from uri.paste import *
from util.exception import *
from api.decorators import require_form_args
from api.decorators import require_login_api
from api.decorators import optional_login_api
import constants.api
import database.attachment
import database.paste
import database.user
import logging
import util.cryptography


@app.route(PasteSubmitURI.path, methods=['POST'])
@require_form_args(['contents'], allow_blank_values=True)
@optional_login_api
def submit_paste():
    """
    Endpoint for submitting a new paste.
    """
    if config.REQUIRE_LOGIN_TO_PASTE and not current_user.is_authenticated:
        return (
            flask.jsonify(constants.api.UNAUTHENTICATED_PASTES_DISABLED_FAILURE),
            constants.api.UNAUTHENTICATED_PASTES_DISABLED_FAILURE_CODE,
        )

    data = flask.request.get_json()

    if not config.ENABLE_PASTE_ATTACHMENTS and len(data.get('attachments', [])) > 0:
        return (
            flask.jsonify(constants.api.PASTE_ATTACHMENTS_DISABLED_FAILURE),
            constants.api.PASTE_ATTACHMENTS_DISABLED_FAILURE_CODE,
        )

    if config.REQUIRE_LOGIN_TO_ATTACH and not current_user.is_authenticated and len(data.get('attachments', [])) > 0:
        return (
            flask.jsonify(constants.api.PASTE_ATTACHMENTS_DISABLED_FAILURE),
            constants.api.PASTE_ATTACHMENTS_DISABLED_FAILURE_CODE,
        )

    is_attachment_too_large = [
        # The data is encoded as a string: each character takes 1 B
        # The base64-encoded string is at 4/3x larger in size than the raw file
        len(attachment.get('data', '')) * 3 / 4.0 > config.MAX_ATTACHMENT_SIZE * 1000 * 1000
        for attachment in data.get('attachments', [])
    ]
    if any(is_attachment_too_large) and config.MAX_ATTACHMENT_SIZE > 0:
        return (
            flask.jsonify(constants.api.PASTE_ATTACHMENT_TOO_LARGE_FAILURE),
            constants.api.PASTE_ATTACHMENT_TOO_LARGE_FAILURE_CODE,
        )

    try:
        new_paste = database.paste.create_new_paste(
            contents=data.get('contents'),
            user_id=current_user.user_id if current_user.is_authenticated else None,
            expiry_time=data.get('expiry_time'),
            title=data.get('title'),
            language=data.get('language'),
            password=data.get('password'),
            # The paste is considered an API post if any of the following conditions are met:
            # (1) The referrer is null.
            # (2) The Home or PastePostInterface URIs are *not* contained within the referrer string (if a paste was
            # posted via the web interface, this is where the user should be coming from, unless the client performed
            # some black magic and spoofed the referrer string or something equally sketchy).
            is_api_post=not flask.request.referrer or not any(
                [uri in flask.request.referrer for uri in [HomeURI.full_uri(), PastePostInterfaceURI.full_uri()]]
            ),
        )
        new_attachments = [
            database.attachment.create_new_attachment(
                paste_id=new_paste.paste_id,
                file_name=attachment.get('name'),
                file_size=attachment.get('size'),
                mime_type=attachment.get('mime_type'),
                file_data=attachment.get('data'),
            )
            for attachment in data.get('attachments', [])
        ]
        resp_data = new_paste.as_dict().copy()
        resp_data['deactivation_token'] = new_paste.deactivation_token
        resp_data['attachments'] = [
            {
                'name': attachment.file_name,
                'size': attachment.file_size,
                'mime_type': attachment.mime_type,
            }
            for attachment in new_attachments
        ]
        return flask.jsonify(resp_data), constants.api.SUCCESS_CODE
    except:
        logging.exception('')
        return flask.jsonify(constants.api.UNDEFINED_FAILURE), constants.api.UNDEFINED_FAILURE_CODE


@app.route(PasteDeactivateURI.path, methods=['POST'])
@require_form_args(['paste_id'])
@optional_login_api
def deactivate_paste():
    """
    Endpoint for deactivating an existing paste.
    The user can deactivate a paste with this endpoint in two ways:
    (1) Supply a deactivation token in the request, or
    (2) Be currently logged in, and own the paste.
    """
    data = flask.request.get_json()
    try:
        paste = database.paste.get_paste_by_id(util.cryptography.get_decid(data['paste_id']), active_only=True)
        if (current_user.is_authenticated and current_user.user_id == paste.user_id) or data.get('deactivation_token') == paste.deactivation_token:
            database.paste.deactivate_paste(paste.paste_id)
            return flask.jsonify({
                constants.api.RESULT: constants.api.RESULT_SUCCESS,
                constants.api.MESSAGE: None,
                'paste_id': util.cryptography.get_id_repr(paste.paste_id),
            }), constants.api.SUCCESS_CODE
        fail_msg = 'User does not own requested paste' if current_user.is_authenticated else 'Deactivation token is invalid'
        return flask.jsonify({
            constants.api.RESULT: constants.api.RESULT_FAULURE,
            constants.api.MESSAGE: fail_msg,
            constants.api.FAILURE: 'auth_failure',
            'paste_id': util.cryptography.get_id_repr(paste.paste_id),
        }), constants.api.AUTH_FAILURE_CODE
    except (PasteDoesNotExistException, InvalidIDException):
        return flask.jsonify(constants.api.NONEXISTENT_PASTE_FAILURE), constants.api.NONEXISTENT_PASTE_FAILURE_CODE
    except:
        logging.exception('')
        return flask.jsonify(constants.api.UNDEFINED_FAILURE), constants.api.UNDEFINED_FAILURE_CODE


@app.route(PasteSetPasswordURI.path, methods=['POST'])
@require_form_args(['paste_id', 'password'], allow_blank_values=True)
@require_login_api
def set_paste_password():
    """
    Modify a paste's password, unset it, or set a new one.
    """
    data = flask.request.get_json()
    try:
        paste = database.paste.get_paste_by_id(util.cryptography.get_decid(data['paste_id']), active_only=True)
        if paste.user_id != current_user.user_id:
            return flask.jsonify({
                constants.api.RESULT: constants.api.RESULT_FAULURE,
                constants.api.MESSAGE: 'User does not own the specified paste',
                constants.api.FAILURE: 'auth_failure',
                'paste_id': util.cryptography.get_id_repr(paste.paste_id),
            }), constants.api.AUTH_FAILURE_CODE
        database.paste.set_paste_password(paste.paste_id, data['password'])
        return flask.jsonify({
            constants.api.RESULT: constants.api.RESULT_SUCCESS,
            constants.api.MESSAGE: None,
            'paste_id': util.cryptography.get_id_repr(paste.paste_id),
        }), constants.api.SUCCESS_CODE
    except (PasteDoesNotExistException, InvalidIDException):
        return flask.jsonify(constants.api.NONEXISTENT_PASTE_FAILURE), constants.api.NONEXISTENT_PASTE_FAILURE_CODE
    except:
        logging.exception('')
        return flask.jsonify(constants.api.UNDEFINED_FAILURE), constants.api.UNDEFINED_FAILURE_CODE


@app.route(PasteDetailsURI.path, methods=['POST'])
@require_form_args(['paste_id'])
def paste_details():
    """
    Retrieve details for a particular paste ID.
    """
    data = flask.request.get_json()
    try:
        paste = database.paste.get_paste_by_id(util.cryptography.get_decid(data['paste_id']), active_only=True)
        attachments = database.attachment.get_attachments_for_paste(util.cryptography.get_decid(data['paste_id']), active_only=True)
        paste_details_dict = paste.as_dict()
        paste_details_dict['poster_username'] = 'Anonymous'
        paste_details_dict['attachments'] = [
            attachment.as_dict()
            for attachment in attachments
        ]
        if paste.user_id:
            poster = database.user.get_user_by_id(paste.user_id)
            paste_details_dict['poster_username'] = poster.username
        if not paste.password_hash or (data.get('password') and paste.password_hash == util.cryptography.secure_hash(data.get('password'))):
            return flask.jsonify({
                constants.api.RESULT: constants.api.RESULT_SUCCESS,
                constants.api.MESSAGE: None,
                'details': paste_details_dict,
            }), constants.api.SUCCESS_CODE
        else:
            return flask.jsonify({
                constants.api.RESULT: constants.api.RESULT_FAULURE,
                constants.api.MESSAGE: 'Password-protected paste: either no password or wrong password supplied',
                constants.api.FAILURE: 'password_mismatch_failure',
                'details': {},
            }), constants.api.AUTH_FAILURE_CODE
    except (PasteDoesNotExistException, UserDoesNotExistException, InvalidIDException):
        return flask.jsonify(constants.api.NONEXISTENT_PASTE_FAILURE), constants.api.NONEXISTENT_PASTE_FAILURE_CODE
    except:
        logging.exception('')
        return flask.jsonify(constants.api.UNDEFINED_FAILURE), constants.api.UNDEFINED_FAILURE_CODE


@app.route(PastesForUserURI.path, methods=['POST'])
@require_login_api
def pastes_for_user():
    """
    Get all pastes for the currently logged in user.
    """
    try:
        return flask.jsonify({
            constants.api.RESULT: constants.api.RESULT_SUCCESS,
            constants.api.MESSAGE: None,
            'pastes': [
                paste.as_dict()
                for paste in database.paste.get_all_pastes_for_user(current_user.user_id, active_only=True)
            ],
        }), constants.api.SUCCESS_CODE
    except:
        logging.exception('')
        return flask.jsonify(constants.api.UNDEFINED_FAILURE), constants.api.UNDEFINED_FAILURE_CODE


@app.route(RecentPastesURI.path, methods=['POST'])
@require_form_args(['page_num', 'num_per_page'])
def recent_pastes():
    """
    Get details for the most recent pastes.
    """
    try:
        data = flask.request.get_json()
        return flask.jsonify({
            constants.api.RESULT: constants.api.RESULT_SUCCESS,
            constants.api.MESSAGE: None,
            'pastes': [
                paste.as_dict() for paste in database.paste.get_recent_pastes(data['page_num'], data['num_per_page'])
            ],
        }), constants.api.SUCCESS_CODE
    except:
        logging.exception('')
        return flask.jsonify(constants.api.UNDEFINED_FAILURE), constants.api.UNDEFINED_FAILURE_CODE


@app.route(TopPastesURI.path, methods=['POST'])
@require_form_args(['page_num', 'num_per_page'])
def top_pastes():
    """
    Get details for the top pastes.
    """
    try:
        data = flask.request.get_json()
        return flask.jsonify({
            constants.api.RESULT: constants.api.RESULT_SUCCESS,
            constants.api.MESSAGE: None,
            'pastes': [
                paste.as_dict() for paste in database.paste.get_top_pastes(data['page_num'], data['num_per_page'])
            ],
        }), constants.api.SUCCESS_CODE
    except:
        logging.exception('')
        return flask.jsonify(constants.api.UNDEFINED_FAILURE), constants.api.UNDEFINED_FAILURE_CODE
