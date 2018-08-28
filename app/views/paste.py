import flask
import logging

import config
import database.attachment
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


@app.route(PasteAttachmentURI.path, methods=['GET'])
def paste_attachment(paste_id, file_name):
    """
    Download a paste attachment.

    :param paste_id: ID of the paste associated with this attachment
    :param file_name: File name of the attachment
    """
    try:
        attachment = database.attachment.get_attachment_by_name(
            paste_id=util.cryptography.get_decid(paste_id),
            file_name=file_name,
            active_only=True,
        )
        file_path = '{attachments_dir}/{paste_id}/{hash_name}'.format(
            attachments_dir=config.ATTACHMENTS_DIR,
            paste_id=util.cryptography.get_decid(paste_id),
            hash_name=attachment.hash_name,
        )
        if not config.USE_CLOUD_STORAGE:
            contents = open(file_path).read()
        else:
            try:
                import cloudstorage as gcs
                from google.appengine.api import app_identity
                import os
                bucket = os.environ.get('BUCKET_NAME',
                                        app_identity.get_default_gcs_bucket_name())
                gcs_path = '/{}{}'.format(bucket, file_path)
                logging.error('Fetching {}'.format(gcs_path))

                gcs_file = gcs.open(gcs_path)
                contents = gcs_file.read()
                gcs_file.close()
            except:
                logging.exception('Cloud storage fetch failed')

        database.paste.increment_paste_views(util.cryptography.get_decid(paste_id))
        resp = flask.make_response(contents)
        resp.headers['Content-Type'] = attachment.mime_type
        return resp
    except (PasteDoesNotExistException, InvalidIDException):
        return 'No paste with the given ID could be found. ' \
               'It\'s also possible that the paste has been deactivated or has expired.', 404
    except AttachmentDoesNotExistException:
        return 'No attachment with the given file name could be found.', 404
    except:
        logging.exception('Undefined error fetching attachment')
        return 'Undefined error. Please open an issue at https://github.com/LINKIWI/modern-paste/issues', 500


@app.route(PasteArchiveInterfaceURI.path, methods=['GET'])
@render_view
def paste_archive():
    """
    View recent and top pastes in a paginated format.
    """
    return 'paste/archive.html', {}
