import util.testing

import database.paste
import database.attachment
from util.exception import *


class TestAttachment(util.testing.DatabaseTestCase):
    def test_create_new_attachment(self):
        paste = util.testing.PasteFactory.generate()
        file_name = util.testing.random_alphanumeric_string()
        attachment = database.attachment.create_new_attachment(
            paste_id=paste.paste_id,
            file_name=file_name,
        )
        self.assertGreater(attachment.attachment_id, -1)
        self.assertEqual(paste.paste_id, attachment.paste_id)
        self.assertEqual(file_name, attachment.file_name)

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
