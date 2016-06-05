# User


class UsernameNotAvailableException(Exception):
    pass


class UserDoesNotExistException(Exception):
    pass


class InvalidEmailException(Exception):
    pass


# Paste


class PasteDoesNotExistException(Exception):
    pass


# Attachment


class AttachmentDoesNotExistException(Exception):
    pass


# Cryptography


class InvalidIDException(Exception):
    pass
