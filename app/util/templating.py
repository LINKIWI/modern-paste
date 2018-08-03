import inspect
import sys
from collections import OrderedDict

import config
import constants
import uri
import util.cryptography
from modern_paste import app


@app.context_processor
def add_config():
    """
    Templating utility to retrieve specific configuration information.

    Currently injected:

        enabled_user_registration
        auth_method
    """
    return dict(auth_method=config.AUTH_METHOD,
                enable_user_registration=config.ENABLE_USER_REGISTRATION)


@app.context_processor
def import_static_resources():
    """
    Templating utility to handle build environment-specific static resource (CSS and JS) imports.
    Javascript loading can be optionally deferred by using the HTML script defer attribute.
    Set the config.BUILD_ENVIRONMENT parameter, then use as

        {{ import_js(['my_js.js', 'my_other_js.js', ...])|safe }}
        {{ import_css(['colors.css', 'fonts.css', ...])|safe }}

    Adding "safe" at the end is required so that Jinja understands how to handle the HTML tags.
    """
    css_import_string = '<link rel="stylesheet" type="text/css" href="{url}">'
    js_import_string = '<script src="{url}" type="text/javascript"></script>'
    js_defer_import_string = '<script src="{url}" type="text/javascript" defer></script>'

    def _css_import_path(path):
        if path.startswith('//'):
            # Externally hosted resources
            return css_import_string.format(url=path)
        if path.startswith('lib'):
            return css_import_string.format(url='/static/{path}'.format(path=path))
        return css_import_string.format(url='/static/build/css/{path}'.format(path=path))

    def import_css(import_paths):
        return '\n'.join(list(OrderedDict.fromkeys(map(_css_import_path, import_paths))))

    def _js_import_path(path, import_string):
        if path.startswith('//'):
            # Externally hosted resources
            return import_string.format(url=path)
        if path.startswith('lib'):
            return import_string.format(url='/static/{path}'.format(path=path))
        if config.BUILD_ENVIRONMENT == constants.build_environment.PROD:
            if path.count('/') == 2:  # Multipart controller
                controller_namespace = path.split('/')
                controller_name = controller_namespace[1][0].upper() + controller_namespace[1][1:] + 'Controller.js'
                return import_string.format(url='/static/build/js/{js_module}/{path}'.format(
                    js_module=controller_namespace[0],
                    path=controller_name,
                ))
            return import_string.format(url='/static/build/js/{path}'.format(path=path))
        return import_string.format(url='/static/js/{path}'.format(path=path))

    def import_js(import_paths, defer=False):
        return '\n'.join(list(OrderedDict.fromkeys(
            [
                _js_import_path(path, js_defer_import_string if defer else js_import_string)
                for path in import_paths
                if config.BUILD_ENVIRONMENT != constants.build_environment.PROD or not path.startswith('universal/')
            ]
        )))

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


@app.context_processor
def get_id_repr():
    """
    Templating utility to encode any ID in the form required by the application, as specified by
    config.USE_ENCRYPTED_IDS. This function simply exports util.cryptography.get_id_repr.
    """
    return dict(id_repr=util.cryptography.get_id_repr)


@app.context_processor
def get_all_uris():
    """
    Templating utility to retrieve all available URIs, mapping modules to URI classes.
    Used ultimately to store all URI paths in the template for easy retrieval by Javascript.

        {{ all_uris() }}
    """
    return dict(all_uris=lambda: {
        uri_module: filter(
            lambda module_name: module_name.endswith('URI') and len(module_name) > 3,
            map(lambda module_pair: module_pair[0], inspect.getmembers(sys.modules['uri.' + uri_module])),
        )
        for uri_module in filter(
            lambda mod: not mod.startswith('__'),
            dir(uri),
        )
    })
