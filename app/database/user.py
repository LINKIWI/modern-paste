import database.paste
import models
import util.cryptography
import util.string
from modern_paste import login_manager
from modern_paste import session
from util.exception import *


def create_new_user(username, password, signup_ip, name=None, email=None):
    """
    Creates a new user with the specified username and password.

    :param username: Requested username of the new user
    :param password: Password for the new user
    :param signup_ip: IP address from which the user signed up
    :param name: Name of the user (optional)
    :param email: Email of the user (optional)
    :return: Newly created User object
    :raises InvalidEmailException: If an invalid email is passed
    :raises UsernameNotAvailableException: If the username is not available
    """
    # Input validation
    if not is_username_available(username):
        raise UsernameNotAvailableException('The username {username} is not available'.format(username=username))
    if email and not is_email_address_valid(email):
        raise InvalidEmailException('{email_addr} is not a valid email address'.format(email_addr=email))

    new_user = models.User(
        signup_ip=signup_ip,
        username=username,
        password_hash=util.cryptography.secure_hash(password),
        name=name,
        email=email,
    )
    session.add(new_user)
    session.commit()
    return new_user


def update_user_details(user_id, name, email, new_password):
    """
    Update an existing user, identified by user_id, with the provided fields. If name or email is None, this will
    remove these fields from the user entry. If new_password is None, the user's password will not be updated.

    :param user_id: User ID of the user to update
    :param name: Updated name, can be empty string or None to indicate no update
    :param email: Updated email, can be empty string or None to indicate no update
    :param new_password: New password, if updating the user's password
    :return: models.User object representing the updated user
    :raises InvalidEmailException: If an invalid email is passed
    """
    if email and not is_email_address_valid(email):
        raise InvalidEmailException('{email_addr} is not a valid email address'.format(email_addr=email))

    user = get_user_by_id(user_id, active_only=True)
    user.name = name
    user.email = email
    if new_password:
        user.password_hash = util.cryptography.secure_hash(new_password)
    session.commit()
    return user


def get_user_by_id(user_id, active_only=False):
    """
    Get a User object by user_id, whose attributes match those in the database.

    :param user_id: User ID to query by
    :param active_only: Set this flag to True to only query for active users
    :return: User object for that user ID
    :raises UserDoesNotExistException: If no user exists with the given user_id
    """
    if active_only:
        user = models.User.query.filter_by(user_id=user_id, is_active=True).first()
    else:
        user = models.User.query.filter_by(user_id=user_id).first()
    if not user:
        raise UserDoesNotExistException('No user with user_id {user_id} exists'.format(user_id=user_id))
    return user


def get_user_by_username(username, active_only=False):
    """
    Get a User object by username, whose attributes match those in the database.

    :param username: Username to query by
    :param active_only: Set this flag to True to only query for active users
    :return: User object for that username
    :raises UserDoesNotExistException: If no user exists with the given username
    """
    if active_only:
        user = models.User.query.filter_by(username=username.lower(), is_active=True).first()
    else:
        user = models.User.query.filter_by(username=username.lower()).first()
    if not user:
        raise UserDoesNotExistException('No user with username {username} exists'.format(username=username))
    return user


def get_user_by_api_key(api_key, active_only=False):
    """
    Get a User object by api_key, whose attributes match those in the database.

    :param api_key: API key to query by
    :param active_only: Set this flag to True to only query for active users
    :return: User object for that user ID
    :raises UserDoesNotExistException: If no user exists with the given user_id
    """
    if active_only:
        user = models.User.query.filter_by(api_key=api_key, is_active=True).first()
    else:
        user = models.User.query.filter_by(api_key=api_key).first()
    if not user:
        raise UserDoesNotExistException('No user with api_key {api_key} exists'.format(api_key=api_key))
    return user


def generate_new_api_key(user_id):
    """
    Generate a new API key for the user.

    :param user_id: User ID for which to generate a new API key
    :return: User object for that user ID with a modified API key
    :raises UserDoesNotExistException: If no user exists with the given user_id
    """
    user = get_user_by_id(user_id)
    user.api_key = util.string.random_alphanumeric_string(length=64)
    session.commit()
    return user


def authenticate_user(username, password):
    """
    Authenticate a user with a username and password. This function only checks if the
    credentials are correct.

    :param username: Username to check
    :param password: Plain text password to authenticate against
    :return: True if the credential pair is valid; False otherwise
    :raises UserDoesNotExistException: If no user exists with the given username
    """
    user = get_user_by_username(username)
    return user.is_active and util.cryptography.secure_hash(password) == user.password_hash


def deactivate_user(user_id):
    """
    Deactivate the specified user by ID. This procedure also deactivates all of the user's pastes.

    :param user_id: User ID to deactivate
    :return: An instance of models.User of the deactivated user
    :raises UserDoesNotExistException: If the user does not exist
    """
    user = get_user_by_id(user_id)
    user.is_active = False
    session.commit()
    for paste in database.paste.get_all_pastes_for_user(user.user_id, active_only=True):
        database.paste.deactivate_paste(paste.paste_id)
    return user


def is_username_available(username):
    """
    Arises from uniqueness constraint on username column.

    :param username: Username to check for availability
    :return: True if the username is available; False otherwise
    """
    return models.User.query.filter_by(username=username.lower()).first() is None


def is_email_address_valid(email_addr):
    """
    Validate that the input is an email address. This won't catch all error cases, but will catch
    the most outrageous ones. I believe in the fundamental goodwill of humanity, e.g. that users
    will not deliberately enter a stupid email address like aa\s\d\@derp..com

    :param email_addr: Email address, type str
    :return: True if the email address is valid, False otherwise
    """
    if ' ' in email_addr:
        return False
    separated_email_addr = tuple(email_addr.split('@'))
    if len(separated_email_addr) != 2:
        return False
    addr, domain = separated_email_addr
    if not len(addr) or not len(domain) or '.' not in domain:
        return False
    return True


@login_manager.user_loader
def load_user(user_id):
    """
    Flask-login requires implementation of this method, which returns a User model
    object when passed a user ID.

    :param user_id: User ID to load.
    """
    try:
        return get_user_by_id(user_id)
    except UserDoesNotExistException:
        return None


def scrub_inactive_users():
    """
    Goes through the database and deletes all users that are inactive. This method is not intended to be called from
    within the application, but rather externally either manually or via a script/cron job.

    For example, in a Python shell:
        > import database.user
        > database.paste.scrub_inactive_users()
    """
    models.User.query.filter_by(is_active=False).delete()
