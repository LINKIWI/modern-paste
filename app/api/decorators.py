from functools import wraps

from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask_login import current_user
from flask_login import login_user
from requests.utils import quote

import config
import database.user
from constants.api import *
from uri.user import UserLoginInterfaceURI
from util.exception import *


def context_config():
    """
    Dictionary of the context that should be made available to all templates rendered with @render_view.
    By default, all fields in config are included.
    """
    return {
        config_item: getattr(config, config_item)
        for config_item in dir(config)
        if config_item == config_item.upper()
    }


def render_view(func):
    """
    Render this view endpoint's specified template with the provided context, with additional context parameters
    as specified by context_config().

        @app.route('/', methods=['GET'])
        @render_view
        def view_function():
            return 'template_name.html', {'context': 'details'}
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        response = func(*args, **kwargs)
        if not isinstance(response, tuple):
            return response
        template, context = response
        if 'config' in context:
            context['config'].update(context_config())
        else:
            context['config'] = context_config()
        return render_template(template, **context)
    return decorated_view


def require_form_args(form_args, allow_blank_values=False, strict_params=False):
    """
    Require this POST endpoint function to be requested with at least the specified parameters in its JSON body.

    Example usage for an endpoint that requires, at minimum, the params 'username' and 'password':

     @app.route('/', methods=['POST'])
     @require_form_args(['username', 'password'])
     def view_function():
        pass

    On failure, returns HTTP status code 400 with the predefined INCOMPLETE_PARAMS_FAILURE JSON response.

    :param form_args: Comma-separated strings representing required POST params.
    :param allow_blank_values: True to explicitly consider an empty value as a valid param value.
    :param strict_params: True to check if the POST request params are strictly equal to form_args.
                          False by default, thereby considering the request valid if there are extra arguments.
    """
    def decorator(func):
        @wraps(func)
        def abort_if_invalid_args(*args, **kwargs):
            if (len(form_args) > 0 and not request.get_json()) or (not strict_params and not set(form_args).issubset(request.get_json().keys())) or (strict_params and set(form_args) != set(request.get_json().keys())) or (not allow_blank_values and not all([request.get_json()[arg] is not None and len(unicode(request.get_json()[arg])) > 0 for arg in form_args])):
                return jsonify(INCOMPLETE_PARAMS_FAILURE), INCOMPLETE_PARAMS_FAILURE_CODE
            return func(*args, **kwargs)
        return abort_if_invalid_args
    return decorator


def require_login_api(func):
    """
    A custom implementation of Flask-login's built-in @login_required decorator.
    This decorator will allow usage of the API endpoint if the user is either currently logged in via the app
    or if the user authenticates with an API key in the POST JSON parameters and local auth is used.
    This implementation overrides the behavior taken when the current user is not authenticated by
    returning the predefined AUTH_FAILURE JSON response with HTTP status code 401.
    This decorator is intended for use with API endpoints.
    """
    @wraps(func)
    def decorator(*args, **kwargs):
        data = request.get_json()
        if current_user.is_authenticated:
            return func(*args, **kwargs)
        try:
            if config.AUTH_METHOD == 'local' and data and data.get('api_key'):
                user = database.user.get_user_by_api_key(data['api_key'], active_only=True)
                login_user(user)
                del data['api_key']
                request.get_json = lambda: data
                return func(*args, **kwargs)
        except UserDoesNotExistException:
            return jsonify(AUTH_FAILURE), AUTH_FAILURE_CODE
        return jsonify(AUTH_FAILURE), AUTH_FAILURE_CODE
    return decorator


def optional_login_api(func):
    """
    This decorator is similar in behavior to require_login_api, but is intended for use with endpoints that offer
    extended functionality with a login, but can still be used without any authentication.
    The decorator will set current_user if authentication via an API key is provided and local auth is used, and will continue without error
    otherwise.
    This decorator is intended for use with API endpoints.
    """
    @wraps(func)
    def decorator(*args, **kwargs):
        data = request.get_json()
        if current_user.is_authenticated:
            return func(*args, **kwargs)
        try:
            if config.AUTH_METHOD == 'local' and data and data.get('api_key'):
                user = database.user.get_user_by_api_key(data['api_key'], active_only=True)
                login_user(user)
                del data['api_key']
                request.get_json = lambda: data
                return func(*args, **kwargs)
        except UserDoesNotExistException:
            return jsonify(AUTH_FAILURE), AUTH_FAILURE_CODE
        return func(*args, **kwargs)
    return decorator


def require_login_frontend(only_if=True):
    """
    Same logic as the API require_login, but this decorator is intended for use for frontend interfaces.
    It returns a redirect to the login page, along with a post-login redirect_url as a GET parameter.

    :param only_if: Optionally specify a boolean condition that needs to be true for the frontend login to be required.
                    This is semantically equivalent to "require login for this view endpoint only if <condition>,
                    otherwise, no login is required"
    """
    def decorator(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated and only_if:
                return redirect(UserLoginInterfaceURI.uri(redirect_url=quote(request.url, safe='')))
            return func(*args, **kwargs)
        return decorated_view
    return decorator


def hide_if_logged_in(redirect_uri):
    """
    If the user attempts to access this frontend endpoint but is already logged in, redirect to the specified URI.
    """
    def decorator(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if current_user.is_authenticated:
                return redirect(redirect_uri)
            return func(*args, **kwargs)
        return decorated_view
    return decorator


def require_local_auth(func):
    """
    Makes the current API endpoint only work with local auth, otherwise returns an error.
    """
    @wraps(func)
    def decorator(*args, **kwargs):
        if config.AUTH_METHOD != 'local':
            return jsonify(AUTH_METHOD_DISABLED_FAILURE), AUTH_METHOD_DISABLED_FAILURE_CODE
        return func(*args, **kwargs)
    return decorator
