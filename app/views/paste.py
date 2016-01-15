import flask

from modern_paste import app

import database.paste
from uri.main import *
from uri.paste import *
from api.decorators import render_view
from util.exception import *
import util.cryptography


@app.route(HomeURI.path, methods=['GET'])
@app.route(PastePostInterfaceURI.path, methods=['GET'])
@render_view
def paste_post():
    """
    Default interface for posting a new paste.
    """
    return 'paste/post.html', {}


@app.route(PasteViewInterfaceURI.path, methods=['GET'])
@render_view
def paste_view(paste_id):
    """
    Default interface for viewing a paste.

    :param paste_id: Encid or decid of the paste to look up; supplied in the URL
    """
    try:
        paste = database.paste.get_paste_by_id(paste_id)
        assert paste.is_active
    except (PasteDoesNotExistException, AssertionError):
        return 'paste/nonexistent.html', {}

    return 'paste/view.html', {
        'paste_id': paste_id,
        'paste_language': paste.language,
    }


@app.route(PasteViewRawInterfaceURI.path, methods=['GET'])
def paste_view_raw(paste_id):
    """
    View a raw paste as plain text.

    :param paste_id: Encid or decid of the paste to look up; supplied in the URL
    """
    try:
        paste = database.paste.get_paste_by_id(paste_id)
        if not paste.is_active:
            raise PasteDoesNotExistException

        password_protection_error = 'In order to view the raw contents of a password-protected paste, ' \
                                    'you must supply the password (in plain text) as a GET parameter in the URL, e.g. ' \
                                    '{example}'.format(example=PasteViewRawInterfaceURI.full_uri(paste_id=paste_id, password='PASTE_PASSWORD_HERE'))
        invalid_password_error = 'The password you supplied for this paste is not correct.'
        if paste.password_hash and not flask.request.args.get('password'):
            return flask.Response(password_protection_error, mimetype='text/plain')
        if paste.password_hash and util.cryptography.secure_hash(flask.request.args.get('password')) != paste.password_hash:
            return flask.Response(invalid_password_error, mimetype='text/plain')

        return flask.Response(paste.contents, mimetype='text/plain')
    except PasteDoesNotExistException:
        return flask.Response('This paste either does not exist or has been deleted.', mimetype='text/plain')
