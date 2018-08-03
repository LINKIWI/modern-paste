import config
from uri.misc import APIDocumentationInterfaceURI


# Result of call
RESULT = 'success'
RESULT_SUCCESS = True
RESULT_FAULURE = False
MESSAGE = 'message'
FAILURE = 'failure'
SUCCESS_CODE = 200


# Predefined JSON responses
# Ensure that the generic error responses documentation in app/templates/api_documentation.json is updated to reflect
# the error responses in this file.
AUTH_FAILURE = {
    RESULT: RESULT_FAULURE,
    MESSAGE: 'User needs to be authenticated to complete this request',
    FAILURE: 'auth_failure',
}
AUTH_FAILURE_CODE = 401

INCOMPLETE_PARAMS_FAILURE = {
    RESULT: RESULT_FAULURE,
    MESSAGE: 'Required params are missing',
    FAILURE: 'incomplete_params_failure',
}
INCOMPLETE_PARAMS_FAILURE_CODE = 400

NONEXISTENT_USER_FAILURE = {
    RESULT: RESULT_FAULURE,
    MESSAGE: 'User does not exist',
    FAILURE: 'nonexistent_user_failure',
}
NONEXISTENT_USER_FAILURE_CODE = 404

NONEXISTENT_PASTE_FAILURE = {
    RESULT: RESULT_FAULURE,
    MESSAGE: 'Paste does not exist',
    FAILURE: 'nonexistent_paste_failure',
}
NONEXISTENT_PASTE_FAILURE_CODE = 404

UNAUTHENTICATED_PASTES_DISABLED_FAILURE = {
    RESULT: RESULT_FAULURE,
    MESSAGE: 'The server administrator has required that users be signed in to post a paste. If you have an account, '
             'authenticate this paste with an API key to post a paste. See {api_url} for more details.'.format(
                 api_url=APIDocumentationInterfaceURI.uri(),
             ),
    FAILURE: 'unauthenticated_pastes_disabled_failure',
}
UNAUTHENTICATED_PASTES_DISABLED_FAILURE_CODE = 403

USER_REGISTRATION_DISABLED_FAILURE = {
    RESULT: RESULT_FAULURE,
    MESSAGE: 'The server administrator has disabled new user registration.',
    FAILURE: 'user_registration_disabled_failure',
}
USER_REGISTRATION_DISABLED_FAILURE_CODE = 403

AUTH_METHOD_DISABLED_FAILURE = {
    RESULT: RESULT_FAULURE,
    MESSAGE: 'The auth method you attempted to use is disabled on this server.',
    FAILURE: 'auth_method_disabled_failure'
}
AUTH_METHOD_DISABLED_FAILURE_CODE = 403

PASTE_ATTACHMENTS_DISABLED_FAILURE = {
    RESULT: RESULT_FAULURE,
    MESSAGE: 'The server administrator has disabled paste attachments.',
    FAILURE: 'paste_attachments_disabled_failure',
}
PASTE_ATTACHMENTS_DISABLED_FAILURE_CODE = 400

PASTE_ATTACHMENT_TOO_LARGE_FAILURE = {
    RESULT: RESULT_FAULURE,
    MESSAGE: 'The paste attachment is too large. The maximum allowable size is {max_size} MB.'.format(max_size=config.MAX_ATTACHMENT_SIZE),
    FAILURE: 'paste_attachment_too_large_failure',
}
PASTE_ATTACHMENT_TOO_LARGE_FAILURE_CODE = 414

UNDEFINED_FAILURE = {
    RESULT: RESULT_FAULURE,
    MESSAGE: 'Undefined server-side failure',
    FAILURE: 'undefined_failure',
}
UNDEFINED_FAILURE_CODE = 500
