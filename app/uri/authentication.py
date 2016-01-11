from base_uri import URI


class LoginUserURI(URI):
    api_endpoint = True
    path = '/api/authentication/login'


class LogoutUserURI(URI):
    api_endpoint = True
    path = '/api/authentication/logout'


class AuthStatusURI(URI):
    api_endpoint = True
    path = '/api/authentication/status'
