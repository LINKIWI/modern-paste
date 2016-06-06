import util.cryptography
from modern_paste import db


class Attachment(db.Model):
    __tablename__ = 'attachment'

    attachment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    paste_id = db.Column(db.Integer, index=True)
    file_name = db.Column(db.Text)
    hash_name = db.Column(db.Text)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.Text)

    def __init__(
        self,
        paste_id,
        file_name,
        file_size,
        mime_type,
    ):
        self.paste_id = paste_id
        self.file_name = file_name
        self.hash_name = util.cryptography.secure_hash(file_name)
        self.file_size = file_size
        self.mime_type = mime_type

    def as_dict(self):
        """
        Represent this attachment as an easily JSON-serializable dictionary.

        :return: Dictionary of attachment properties
        """
        return {
            'paste_id_repr': util.cryptography.get_id_repr(self.paste_id),
            'file_name': self.file_name,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
        }
