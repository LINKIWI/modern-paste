from modern_paste import app
from collections import OrderedDict

import config
import constants


@app.context_processor
def import_static_resource():
    """
    TODO
    """
    css_import_string = '<link rel="stylesheet" type="text/css" href="{url}">'
    js_import_string = '<script src="{url}" type="text/javascript"></script>'

    def import_css(import_paths):
        return '\n'.join(list(OrderedDict.fromkeys([
             css_import_string.format(url='/static/build/{path}'.format(path=path))
             for path in import_paths
         ])))

    def js_import_path(path):
        if path.startswith('//'):
            # Externally hosted resources
            return path
        if config.BUILD_ENVIRONMENT == constants.build_environment.PROD:
            return js_import_string.format(url='/static/build/js.js')
        return js_import_string.format(url='/static/js/{path}'.format(path=path))

    def import_js(import_paths):
        return '\n'.join(list(OrderedDict.fromkeys(map(js_import_path, import_paths))))

    return dict(import_css=import_css, import_js=import_js)


@app.context_processor
def get_uri_path():
    """
    Templating utility to easily retrieve the URI path given the URI module and class name of the
    desired URI. This saves the effort of explicitly retrieving the URI path when building
    the template environment, instead allowing for on-the-fly template-side URI retrievals like:

        {{ uri('user', 'UserCreateURI') }}
        {{ uri('user', 'UserCreateURI', param='value') }}
        {{ full_uri('user', 'UserCreateURI', param='value') }}

    :raises ImportError: If one or both of the URI module or class name is invalid
    """
    def uri(uri_module, uri_name, *args, **kwargs):
        uri_module = __import__('uri.' + uri_module, globals(), locals(), [uri_name], -1)
        uri_class = getattr(uri_module, uri_name)
        return uri_class.uri(*args, **kwargs)

    def full_uri(uri_module, uri_name, *args, **kwargs):
        uri_module = __import__('uri.' + uri_module, globals(), locals(), [uri_name], -1)
        uri_class = getattr(uri_module, uri_name)
        return uri_class.full_uri(*args, **kwargs)

    return dict(uri=uri, full_uri=full_uri)
