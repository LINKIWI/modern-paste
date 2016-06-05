import database.paste
import models
from modern_paste import session
from util.exception import *


def create_new_attachment(paste_id, file_name):
    """
    Create a new database entry for an attachment with the given file_name, associated with a particular paste ID.
    TODO maybe mime type too?

    :param paste_id: Paste ID to associate with this attachment
    :param file_name: Full file name of the attachment (including file extension)
    :return: An instance of models.Attachment describing this attachment entry
    """
    new_attachment = models.Attachment(
        paste_id=paste_id,
        file_name=file_name,
    )
    session.add(new_attachment)
    session.commit()
    return new_attachment


def get_attachment_by_id(attachment_id, active_only=False):
    """
    Retrieve an attachment's details by ID.

    :param attachment_id: ID of the attachment to retrieve
    :param active_only: True to only attempt to retrieve attachments associated with active pastes
    :return: An instance of models.Attachment with the requested ID
    :raises AttachmentDoesNotExistException: If the attachment doesn't exist, or the associated paste doesn't exist,
                                             is deactivated, or has expired
    """
    attachment = models.Attachment.query.filter_by(attachment_id=attachment_id).first()
    if not attachment:
        raise AttachmentDoesNotExistException(
            'No attachment with attachment_id {attachment_id} exists'.format(attachment_id=attachment_id)
        )

    try:
        database.paste.get_paste_by_id(attachment.paste_id, active_only=active_only)
    except PasteDoesNotExistException:
        raise AttachmentDoesNotExistException(
            'The paste with paste_id {paste_id} associated with the attachment with attachment_id {attachment_id} has been deactivated or is expired'.format(
                paste_id=attachment.paste_id,
                attachment_id=attachment_id,
            )
        )

    return attachment


def get_attachments_for_paste(paste_id, active_only=False):
    """
    Retrieve a list of attachments associated with a paste.

    :param paste_id: ID of the paste for which to retrieve a list of attachments entries.
    :param active_only: True to ensure that the paste is active
    :return: A list of models.Attachment objects
    :raises PasteDoesNotExistException: If active_only is True and the paste is deactivated or nonexistent
    """
    return models.Attachment.query.filter_by(
        # This will throw an exception if the associated paste is inactive or nonexistent
        paste_id=database.paste.get_paste_by_id(paste_id=paste_id, active_only=active_only).paste_id,
    ).all()
