from modern_paste import app

import database.paste
from uri.main import *
from uri.paste import *
from api.decorators import render_view
from util.exception import *


@app.route(HomeURI.path, methods=['GET'])
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
