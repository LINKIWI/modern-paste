import models
import util.cryptography
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


def get_user_by_id(user_id):
    """
    Get a User object by user_id, whose attributes match those in the database.

    :param user_id: User ID to query by
    :return: User object for that user ID
    :raises UserDoesNotExistException: If no user exists with the given user_id
    """
    user = models.User.query.filter_by(user_id=user_id).first()
    if not user:
        raise UserDoesNotExistException('No user with user_id {user_id} exists'.format(user_id=user_id))
    return user


def get_user_by_username(username):
    """
    Get a User object by username, whose attributes match those in the database.

    :param username: Username to query by
    :return: User object for that username
    :raises UserDoesNotExistException: If no user exists with the given username
    """
    user = models.User.query.filter_by(username=username.lower()).first()
    if not user:
        raise UserDoesNotExistException('No user with username {username} exists'.format(username=username))
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
    return util.cryptography.secure_hash(password) == user.password_hash


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
