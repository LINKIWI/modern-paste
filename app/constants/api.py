# Result of call
RESULT = 'success'
RESULT_SUCCESS = True
RESULT_FAULURE = False
MESSAGE = 'message'
FAILURE = 'failure'
SUCCESS_CODE = 200


# Predefined JSON responses
AUTH_FAILURE = {
    RESULT: RESULT_FAULURE,
    FAILURE: 'auth_failure',
    MESSAGE: 'User needs to be authenticated to complete this request',
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
NONEXISTENT_USER_FAILURE_CODE = 400
