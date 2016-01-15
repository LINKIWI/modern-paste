import models

from modern_paste import session
from util.exception import *
import util.cryptography


def create_new_paste(contents, user_id=None, expiry_time=None, title=None, language=None, password=None):
    """
    Create a new paste.

    :param user_id: User ID of the paste poster
    :param contents: Contents of the paste
    :param expiry_time: Unix time at which the paste should expire (optional, default to no expiry)
    :param title: Title of the paste (optional)
    :param language: Language of the paste (optional, defaults to plain text)
    :param password: Password of the paste (optional)
    :return: An instance of models.Paste representing the newly added paste.
    """
    new_paste = models.Paste(
        user_id=user_id,
        contents=contents,
        expiry_time=int(expiry_time) if expiry_time is not None else None,
        title=title,
        language=language or 'text',
        password_hash=util.cryptography.secure_hash(password) if password is not None else None,
    )
    session.add(new_paste)
    session.commit()
    return new_paste


def get_paste_by_id(paste_id, active_only=False):
    """
    Get the specified paste by ID.

    :param paste_id: Paste ID to look up
    :param active_only: Set this flag to True to only query for active pastes
    :return: An instance of models.Paste representing the requested paste
    :raises PasteDoesNotExistException: If the paste does not exist
    """
    if active_only:
        paste = models.Paste.query.filter_by(paste_id=paste_id, is_active=True).first()
    else:
        paste = models.Paste.query.filter_by(paste_id=paste_id).first()
    if not paste:
        raise PasteDoesNotExistException('No paste with paste_id {paste_id} exists'.format(paste_id=paste_id))
    return paste


def deactivate_paste(paste_id):
    """
    Deactivate the specified paste by ID.

    :param paste_id: Paste ID to deactivate
    :return: An instance of models.Paste of the deactivated paste
    :raises PasteDoesNotExistException: If the paste does not exist
    """
    paste = get_paste_by_id(paste_id)
    paste.is_active = False
    session.commit()
    return paste


def get_all_pastes_for_user(user_id):
    """
    Gets all pastes for the specified user ID.

    :param user_id: User ID for which to retrieve all the pastes
    :return: A list of models.Paste objects belonging to the user ID (can be an empty list)
    """
    return models.Paste.query.filter_by(user_id=user_id).all()
