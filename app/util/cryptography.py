import base64
from Crypto.Cipher import AES
from Crypto.Hash import SHA256

from modern_paste import app
from util.exception import InvalidIDException


BLOCK_SIZE = 32
PADDING_CHAR = '*'
cipher = AES.new(app.config['ID_ENCRYPTION_KEY'])


def _pad(s):
    return s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING_CHAR


def get_encid(decid):
    """
    Generate an encrypted ID from a decrypted ID

    :param decid: Decrypted ID, type int
    :return: Encrypted ID, type str
    """
    try:
        int(decid)
    except:
        raise InvalidIDException('Decrypted ID must be int-castable')

    # Slashes are not URL-friendly; replace them with dashes
    return base64.b64encode(cipher.encrypt(_pad(str(decid)))).replace('/', '-').replace('+', '~')


def get_decid(encid):
    """
    Generate a decrypted ID from an encrypted ID

    :param encid: Encrypted ID, type str
    :return: Decrypted ID, type int
    """
    try:
        str(encid)
    except:
        raise InvalidIDException('Encrypted ID must be str-castable')

    try:
        return int(cipher.decrypt(base64.b64decode(str(encid).replace('-', '/').replace('~', '+'))).rstrip(PADDING_CHAR))
    except:
        raise InvalidIDException('The encrypted ID is not valid')


def secure_hash(s, iterations=10000):
    """
    Performs several iterations of a SHA256 hash of a plain-text string to generate a secure hash.

    :param s: Input string to hash
    :param iterations: Number of hash iterations to use
    :return: A string representing a secure hash of the string
    """
    hash_result = SHA256.new(data=str(s)).hexdigest()
    for i in range(iterations):
        hash_result = SHA256.new(data=hash_result).hexdigest()
    return hash_result
