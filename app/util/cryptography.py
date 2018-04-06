import base64
from Crypto.Cipher import AES
from Crypto.Hash import SHA256

import config
from util.exception import InvalidIDException


# Source: http://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.197.pdf
# Section 3.1: "The input and output for the AES algorithm each consist of
# *sequences of 128 bits*"  (128 bits == 16 bytes)
BLOCK_SIZE = 16
PADDING_CHAR = '*'
ALTCHARS = '~-'


def _pad(s):
    return s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING_CHAR


def _base64_decode(data):
    """Decode base64, re-adding padding if needed."""
    to_add = len(data) % 4
    if to_add != 0:
        data += b'=' * (4 - to_add)
    return base64.b64decode(data, ALTCHARS)


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
    # Also strip the base64 padding: it can be recovered.
    cipher = AES.new(config.ID_ENCRYPTION_KEY, AES.MODE_CBC, config.ID_ENCRYPTION_IV)
    return base64.b64encode(cipher.encrypt(_pad(str(decid))), ALTCHARS).rstrip('=')


def get_decid(encid, force=False):
    """
    Generate a decrypted ID from an encrypted ID.
    This is a bit of a tricky situation: when configured to use encrypted IDs, the entire application should refuse
    to respond to valid decrypted IDs, and should only consider valid (e.g., decryptable) encrypted IDs. However,
    when the application is configured to use decrypted IDs, it should not throw exceptions when attempting to get
    the decrypted ID of an ID that is already decrypted. Similarly, the application should throw exceptions when
    configured to expect only decrypted IDs, but encounters a (potentially valid) encrypted ID.
    The compromise solution here is to throw exceptions depending on the application's current configuration setting.
    Note that this will cause this function to exhibit different behavior depending on the application's configuration.

    :param encid: Encrypted ID, type str
    :param force: Forcefully decrypt the encid, regardless of the current configuration
    :return: Decrypted ID, type int
    """
    try:
        assert int(encid) > 0
        if not config.USE_ENCRYPTED_IDS:
            # If we're not configured to use encids, we can assume the passed encid is already decrypted
            return encid
    except:
        if not config.USE_ENCRYPTED_IDS and not force:
            # We expected a decid (e.g., an int-castable one)
            raise InvalidIDException('The encrypted ID is not valid')

    try:
        str(encid)
        cipher = AES.new(config.ID_ENCRYPTION_KEY, AES.MODE_CBC, config.ID_ENCRYPTION_IV)
        return int(cipher.decrypt(_base64_decode(str(encid))).rstrip(PADDING_CHAR))
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
        return get_decid(raw_id, force=True)


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
