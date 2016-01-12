from modern_paste import app

from uri.main import *
from uri.paste import *
from api.decorators import render_view


@app.route(HomeURI.path, methods=['GET'])
@render_view
def paste_post():
    return 'paste/post.html', {}


@app.route(PasteViewInterfaceURI.path, methods=['GET'])
@render_view
def paste_view(paste_id):
    return 'paste/view.html', {}
