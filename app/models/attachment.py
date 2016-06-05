from modern_paste import db


class Attachment(db.Model):
    __tablename__ = 'attachment'

    attachment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    paste_id = db.Column(db.Integer, index=True)
    file_name = db.Column(db.Text)

    def __init__(
        self,
        paste_id,
        file_name,
    ):
        self.paste_id = paste_id
        self.file_name = file_name
