import base64
from Crypto.Cipher import AES
from Crypto.Hash import SHA256

import config
from util.exception import InvalidIDException


BLOCK_SIZE = 32
PADDING_CHAR = '*'
cipher = AES.new(config.ID_ENCRYPTION_KEY)


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
    Generate a decrypted ID from an encrypted ID.
    This function makes use of a non-trivial number of try-excepts that I am not proud of.

    :param encid: Encrypted ID, type str
    :return: Decrypted ID, type int
    """
    try:
        assert int(encid) > 0
        # If the "encid" is both int-castable and greater than 0 in value,
        # we can assume it's already a decid, so we can safely return it back.
        return encid
    except:
        try:
            str(encid)
        except:
            raise InvalidIDException('Encrypted ID must be str-castable')
        try:
            return int(cipher.decrypt(base64.b64decode(str(encid).replace('-', '/').replace('~', '+'))).rstrip(PADDING_CHAR))
        except:
            raise InvalidIDException('The encrypted ID is not valid')


def get_id_repr(raw_id):
    """
    Get either an encrypted ID or decrypted ID from the input ID given the application configuration

    :param id: ID to adapt to the current configuration
    :return: Either an encrypted version of the ID or a decrypted version of the ID
    """
    if config.USE_ENCRYPTED_IDS:
        try:
            return get_encid(raw_id)
        except InvalidIDException:
            # If we can't get an encid out of the ID, let's just assume it's already an encid
            # This is relatively unsafe is ok with due diligence in checking inputs before using this method.
            return raw_id
    else:
        return get_decid(raw_id)


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
