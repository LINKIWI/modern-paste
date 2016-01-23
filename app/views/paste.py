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
        paste = database.paste.get_paste_by_id(util.cryptography.get_decid(paste_id), active_only=True)
        database.paste.increment_paste_views(util.cryptography.get_decid(paste_id))
    except (PasteDoesNotExistException, InvalidIDException):
        return 'paste/nonexistent.html', {}

    return 'paste/view.html', {
        'paste_id': paste_id,
        'paste_language': paste.language,
        'deactivation_token': paste.deactivation_token if paste.views == 1 else None
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


@app.route(PasteDeactivateInterfaceURI.path, methods=['GET'])
@render_view
def paste_deactivate(paste_id, deactivation_token):
    """
    Deactive the requested paste by deactivation token and indicate in the UI whether the deactivation was
    successful.

    :param paste_id: ID of the paste to deactivate
    :param deactivation_token: Token associated with that paste
    """
    try:
        return 'paste/deactivate.html', {
            'success': database.paste.get_paste_by_id(
                util.cryptography.get_decid(paste_id),
                active_only=True,
            ).deactivation_token == deactivation_token and database.paste.deactivate_paste(
                util.cryptography.get_decid(paste_id),
            ),
        }
    except:
        return 'paste/deactivate.html', {
            'success': False,
        }


@app.route(PasteArchiveInterfaceURI.path, methods=['GET'])
@render_view
def paste_archive():
    """
    View recent and top pastes in a paginated format.
    """
    return 'paste/archive.html', {}
