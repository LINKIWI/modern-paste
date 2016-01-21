import os
import json

from api.decorators import render_view
from modern_paste import app
from uri.misc import *


@app.route(APIDocumentationInterfaceURI.path, methods=['GET'])
@render_view
def api_documentation_interface():
    api_endpoints = json.loads(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '../templates/misc/api_endpoints.json',
    )).read())['api_endpoints']
    return 'misc/api_documentation.html', {
        'api_endpoints': api_endpoints,
    }
