from modern_paste import db

from util.cryptography import secure_hash


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
        self.hash_name = secure_hash(file_name)
        self.file_size = file_size
        self.mime_type = mime_type
