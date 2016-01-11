from flask import render_template

from modern_paste import app

from uri.main import *
from uri.paste import *


@app.route(HomeURI.path, methods=['GET'])
def paste_post():
    return render_template('paste/post.html')


@app.route(PasteViewInterfaceURI.path, methods=['GET'])
def paste_view(paste_id):
    return render_template('paste/view.html')
