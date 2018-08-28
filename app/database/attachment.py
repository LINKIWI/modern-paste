import base64
import errno
import os
import logging

from werkzeug.utils import secure_filename

import config
import database.paste
import models
from modern_paste import session
from util.exception import *


def create_new_attachment(paste_id, file_name, file_size, mime_type, file_data):
    """
    Create a new database entry for an attachment with the given file_name, associated with a particular paste ID.

    :param paste_id: Paste ID to associate with this attachment
    :param file_name: Raw name of the file
    :param file_size: Size of the file in bytes
    :param mime_type: MIME type of the file
    :param file_data: Binary, base64-encoded file data
    :return: An instance of models.Attachment describing this attachment entry
    :raises PasteDoesNotExistException: If the associated paste does not exist
    """
    # Add an entry into the database describing this file
    new_attachment = models.Attachment(
        paste_id=paste_id,
        file_name=secure_filename(file_name),
        file_size=file_size,
        mime_type=mime_type,
    )

    _store_attachment_file(paste_id, file_data, new_attachment)

    session.add(new_attachment)
    session.commit()

    return new_attachment


def _store_attachment_file(paste_id, attachment_binary_data, attachment):
    """
    Store the attachment on disk.

    :param paste_id: Paste ID to associate with this attachment
    :param attachment_binary_data: Binary, base64-encoded data for this attachment to write to a file
    :param attachment: The attachment file metadata
    """
    # Create the file paths for storage
    save_file_dir = '{attachments_dir}/{paste_id}'.format(
        attachments_dir=config.ATTACHMENTS_DIR,
        # This will throw PasteDoesNotExistException if the paste ID does not exist or is invalid
        # This also protects against malicious users who specify an invalid paste ID
        paste_id=database.paste.get_paste_by_id(paste_id, active_only=True).paste_id,
    )
    save_file_path = '{save_file_dir}/{hash_name}'.format(
        save_file_dir=save_file_dir,
        hash_name=attachment.hash_name,
    )

    if not config.USE_CLOUD_STORAGE:
        # Create the directory if it doesn't already exist
        try:
            os.makedirs(save_file_dir)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

        # Decode and write the attachment's data to a file
        with open(save_file_path, 'w') as attachment_file:
            attachment_file.write(base64.b64decode(attachment_binary_data))
    else:
        try:
            import cloudstorage as gcs
            from google.appengine.api import app_identity
            import os

            bucket = os.environ.get('BUCKET_NAME',
                                    app_identity.get_default_gcs_bucket_name())
            gcs_path = '/{}{}'.format(bucket, save_file_path)
            logging.error('Saving to {}'.format(gcs_path))

            gcs_file = gcs.open(gcs_path, 'w',
                                content_type=attachment.mime_type,
                                retry_params=gcs.RetryParams(backoff_factor=1.1))
            gcs_file.write(str(base64.b64decode(attachment_binary_data)))
            gcs_file.close()
        except:
            logging.exception('Cloud storage store failed')


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
    if not attachment or (active_only and not database.paste.is_paste_active(attachment.paste_id)):
        raise AttachmentDoesNotExistException(
            'No attachment with attachment_id {attachment_id} exists or its associated paste has been deactivated or is expired'.format(
                attachment_id=attachment_id,
            )
        )

    return attachment


def get_attachment_by_name(paste_id, file_name, active_only=False):
    """
    Get an attachment associated with a paste ID by name.

    :param paste_id: ID of the paste associated with this attachment
    :param file_name: Name of the file to retrieve
    :param active_only: True to ensure that the paste is active
    :return: A models.Attachment instance representing the requested attachment
    :raises PasteDoesNotExistException: If active_only is True and the paste is deactivated or nonexistent
    :raises AttachmentDoesNotExistException: If the attachment does not exist
    """
    attachment = models.Attachment.query.filter_by(
        paste_id=database.paste.get_paste_by_id(paste_id, active_only=active_only).paste_id,
        file_name=file_name,
    ).first()
    if not attachment:
        raise AttachmentDoesNotExistException(
            'No attachment with file_name {file_name} for paste_id {paste_id} exists'.format(
                file_name=file_name,
                paste_id=paste_id,
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
