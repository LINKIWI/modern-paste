import os
import json

from api.decorators import render_view
from modern_paste import app
from uri.misc import *


@app.route(APIDocumentationInterfaceURI.path, methods=['GET'])
@render_view
def api_documentation_interface():
    api_documentation_data = json.loads(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '../templates/misc/api_documentation.json',
    )).read())
    return 'misc/api_documentation.html', {
        'api_endpoints': api_documentation_data['api_endpoints'],
        'generic_error_responses': api_documentation_data['generic_error_responses'],
    }
