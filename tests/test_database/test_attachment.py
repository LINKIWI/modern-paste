import errno
import os

import mock

import config
import database.attachment
import database.paste
import util.cryptography
import util.testing
from util.exception import *


class TestAttachment(util.testing.DatabaseTestCase):
    def test_create_new_attachment(self):
        with mock.patch.object(database.attachment, '_store_attachment_file') as mock_store_attachment_file:
            paste = util.testing.PasteFactory.generate()
            attachment = database.attachment.create_new_attachment(
                paste_id=paste.paste_id,
                file_name='file name',
                file_size=12345,
                mime_type='image/png',
                file_data='binary data',
            )
            self.assertGreater(attachment.attachment_id, -1)
            self.assertEqual(paste.paste_id, attachment.paste_id)
            self.assertEqual('file_name', attachment.file_name)
            self.assertEqual(12345, attachment.file_size)
            self.assertEqual('image/png', attachment.mime_type)
            self.assertEqual(util.cryptography.secure_hash('file_name'), attachment.hash_name)
            self.assertEqual(1, mock_store_attachment_file.call_count)
            mock_store_attachment_file.assert_called_with(
                paste.paste_id,
                'binary data',
                attachment.hash_name,
            )

    def test_create_new_attachment_unsafe_file_name(self):
        with mock.patch.object(database.attachment, '_store_attachment_file') as mock_store_attachment_file:
            paste = util.testing.PasteFactory.generate()
            attachment = database.attachment.create_new_attachment(
                paste_id=paste.paste_id,
                file_name='test/.bashrc',  # Sneaky
                file_size=12345,
                mime_type='image/png',
                file_data='binary data',
            )
            self.assertEqual('test_.bashrc', attachment.file_name)
            self.assertEqual(util.cryptography.secure_hash('test_.bashrc'), attachment.hash_name)
            self.assertEqual(1, mock_store_attachment_file.call_count)

    def test_store_attachment_file(self):
        with mock.patch.object(os, 'makedirs') as mock_makedirs, mock.patch('__builtin__.open') as mock_open:
            exception = OSError()
            exception.errno = errno.EEXIST
            mock_makedirs.side_effect = exception

            paste = util.testing.PasteFactory.generate()
            self.assertIsNone(database.attachment._store_attachment_file(paste.paste_id, 'binary data', 'hash name'))
            self.assertEqual(1, mock_makedirs.call_count)
            self.assertEqual(1, mock_open.call_count)

        with mock.patch.object(os, 'makedirs') as mock_makedirs, mock.patch('__builtin__.open') as mock_open:
            exception = OSError()
            exception.errno = errno.EACCES
            mock_makedirs.side_effect = exception

            paste = util.testing.PasteFactory.generate()
            self.assertRaises(
                OSError,
                database.attachment._store_attachment_file,
                paste.paste_id,
                'binary data',
                'hash name',
            )

        with mock.patch.object(os, 'makedirs') as mock_makedirs, mock.patch('__builtin__.open') as mock_open:
            paste = util.testing.PasteFactory.generate()
            self.assertIsNone(database.attachment._store_attachment_file(paste.paste_id, 'binary data', 'hash name'))
            self.assertEqual(1, mock_makedirs.call_count)
            mock_makedirs.assert_called_with('{attachments_dir}/{paste_id}'.format(
                attachments_dir=config.ATTACHMENTS_DIR,
                paste_id=paste.paste_id,
            ))
            self.assertEqual(1, mock_open.call_count)
            mock_open.assert_called_with('{attachments_dir}/{paste_id}/{file_name}'.format(
                attachments_dir=config.ATTACHMENTS_DIR,
                paste_id=paste.paste_id,
                file_name='hash name',
            ), 'w')

    def test_get_attachment_by_id(self):
        self.assertRaises(
            AttachmentDoesNotExistException,
            database.attachment.get_attachment_by_id,
            -1,
        )

        paste = util.testing.PasteFactory.generate()
        attachment = util.testing.AttachmentFactory.generate(paste_id=paste.paste_id)
        self.assertEqual(attachment, database.attachment.get_attachment_by_id(attachment.attachment_id))

        # Attachment should not be fetched if the corresponding paste is deactivated and the active_only flag
        # is specified as True
        database.paste.deactivate_paste(paste.paste_id)
        self.assertRaises(
            AttachmentDoesNotExistException,
            database.attachment.get_attachment_by_id,
            paste.paste_id,
            active_only=True,
        )

    def test_get_attachment_by_name(self):
        self.assertRaises(
            PasteDoesNotExistException,
            database.attachment.get_attachment_by_name,
            paste_id=-1,
            file_name='file_name',
        )

        paste = util.testing.PasteFactory.generate()
        self.assertRaises(
            AttachmentDoesNotExistException,
            database.attachment.get_attachment_by_name,
            paste_id=paste.paste_id,
            file_name='nonexistent',
        )

        attachment = util.testing.AttachmentFactory.generate(paste_id=paste.paste_id)
        queried_attachment = database.attachment.get_attachment_by_name(paste.paste_id, attachment.file_name)
        self.assertEqual(attachment, queried_attachment)

        database.paste.deactivate_paste(paste.paste_id)
        self.assertRaises(
            PasteDoesNotExistException,
            database.attachment.get_attachment_by_name,
            paste_id=paste.paste_id,
            file_name=attachment.file_name,
            active_only=True,
        )

    def test_get_attachments_for_paste(self):
        self.assertRaises(
            PasteDoesNotExistException,
            database.attachment.get_attachments_for_paste,
            -1,
        )

        paste = util.testing.PasteFactory.generate()
        attachments = [
            util.testing.AttachmentFactory.generate(paste_id=paste.paste_id)
            for _ in range(5)
        ]

        queried_attachments = database.attachment.get_attachments_for_paste(paste.paste_id)
        self.assertEqual(5, len(queried_attachments))
        for expect_attachment in attachments:
            self.assertIn(expect_attachment, queried_attachments)

        # Attachments should only be retrieved if the paste is active
        database.paste.deactivate_paste(paste.paste_id)
        self.assertRaises(
            PasteDoesNotExistException,
            database.attachment.get_attachments_for_paste,
            paste.paste_id,
            active_only=True,
        )
