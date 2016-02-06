import flask

import config
import database.paste
import util.cryptography
from api.decorators import render_view
from api.decorators import require_login_frontend
from modern_paste import app
from uri.main import *
from uri.paste import *
from util.exception import *


@app.route(HomeURI.path, methods=['GET'])
@app.route(PastePostInterfaceURI.path, methods=['GET'])
@require_login_frontend(only_if=config.REQUIRE_LOGIN_TO_PASTE)
@render_view
def paste_post():
    """
    Default interface for posting a new paste.
    """
    return 'paste/post.html', {}


@app.route(PasteViewInterfaceURI.path, methods=['GET'])
@app.route(PasteDeactivateInterfaceURI.path, methods=['GET'])
@render_view
def paste_view(paste_id, deactivation_token=None):
    """
    Default interface for viewing a paste or deactivating a paste.

    :param paste_id: Encid or decid of the paste to look up; supplied in the URL
    :param deactivation_token: Deactivation token string for paste if the user is attempting to deactivate.
    """
    try:
        paste = database.paste.get_paste_by_id(util.cryptography.get_decid(paste_id), active_only=True)
        database.paste.increment_paste_views(util.cryptography.get_decid(paste_id))
    except (PasteDoesNotExistException, InvalidIDException):
        return 'paste/nonexistent.html', {}

    return 'paste/view.html', {
        'paste': paste,
        # Display the deactivation token if this is the paste's first view and if it was posted via the web interface
        'show_deactivation_token': paste.views == 1 and not paste.is_api_post,
        # User-supplied deactivation token for manual deactivation
        'deactivation_token': deactivation_token,
    }


@app.route(PasteViewRawInterfaceURI.path, methods=['GET'])
def paste_view_raw(paste_id):
    """
    View a raw paste as plain text.

    :param paste_id: Encid or decid of the paste to look up; supplied in the URL
    """
    try:
        paste = database.paste.get_paste_by_id(util.cryptography.get_decid(paste_id), active_only=True)

        password_protection_error = 'In order to view the raw contents of a password-protected paste, ' \
                                    'you must supply the password (in plain text) as a GET parameter in the URL, e.g. ' \
                                    '{example}'.format(example=PasteViewRawInterfaceURI.full_uri(paste_id=paste_id, password='PASTE_PASSWORD_HERE'))
        invalid_password_error = 'The password you supplied for this paste is not correct.'
        if paste.password_hash and not flask.request.args.get('password'):
            return flask.Response(password_protection_error, mimetype='text/plain')
        if paste.password_hash and util.cryptography.secure_hash(flask.request.args.get('password')) != paste.password_hash:
            return flask.Response(invalid_password_error, mimetype='text/plain')

        database.paste.increment_paste_views(util.cryptography.get_decid(paste_id))
        return flask.Response(paste.contents, mimetype='text/plain')
    except (PasteDoesNotExistException, InvalidIDException):
        return flask.Response('This paste either does not exist or has been deleted.', mimetype='text/plain')


@app.route(PasteArchiveInterfaceURI.path, methods=['GET'])
@render_view
def paste_archive():
    """
    View recent and top pastes in a paginated format.
    """
    return 'paste/archive.html', {}
