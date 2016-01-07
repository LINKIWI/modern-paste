from base_uri import URI


class UserLoginURI(URI):
    path = '/login'


class UserLogoutURI(URI):
    path = '/logout'


class UserRegisterURI(URI):
    path = '/register'


class UserCreateURI(URI):
    api_endpoint = True
    path = '/api/user/create'


class UserDeactivateURI(URI):
    api_endpoint = True
    path = '/api/user/deactivate'


class CheckUsernameAvailabilityURI(URI):
    api_endpoint = True
    path = '/api/user/check_username_availability'


class ValidateEmailAddressURI(URI):
    api_endpoint = True
    path = '/api/user/validate_email_address'
