from flask import redirect
from flask.ext.login import logout_user

from api.decorators import hide_if_logged_in
from api.decorators import render_view
from modern_paste import app
from uri.misc import *


@app.route(APIDocumentationInterfaceURI.path, methods=['GET'])
@render_view
def api_documentation_interface():
    return 'misc/api_documentation.html', {}
