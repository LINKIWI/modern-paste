from functools import wraps
from requests.utils import quote

from flask import jsonify
from flask import redirect
from flask import request
from flask.ext.login import current_user

from uri.user import UserLoginURI
from constants.api import *


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
            if (not strict_params and not set(form_args).issubset(request.get_json().keys())) or (strict_params and set(form_args) != set(request.get_json().keys())) or (not allow_blank_values and not all([request.get_json()[arg] is not None and len(str(request.get_json()[arg])) > 0 for arg in form_args])):
                return jsonify(INCOMPLETE_PARAMS_FAILURE), INCOMPLETE_PARAMS_FAILURE_CODE
            return func(*args, **kwargs)
        return abort_if_invalid_args
    return decorator


def require_login_api(func):
    """
    A custom implementation of Flask-login's built-in @login_required decorator.
    This implementation overrides the behavior taken when the current user is not authenticated by
    returning the predefined AUTH_FAILURE JSON response with HTTP status code 403.
    This decorator is intended for use with API endpoints.
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify(AUTH_FAILURE), AUTH_FAILURE_CODE
        return func(*args, **kwargs)
    return decorated_view


def require_login_frontend(func):
    """
    Same logic as the API require_login, but this decorator is intended for use for frontend interfaces.
    It returns a redirect to the login page, along with a post-login redirect_url as a GET parameter.
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(UserLoginURI.uri(redirect_url=quote(request.url, safe='')))
        return func(*args, **kwargs)
    return decorated_view


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
