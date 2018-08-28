import random


def random_alphanumeric_string(length=64):
    """
    Generate a random alphanumeric string of the specified length.

    :param length: Length of the random string
    :return: A random string of length length containing only alphabetic and numeric characters
    """
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    numbers = '0123456789'
    return ''.join([random.choice(list(alphabet) + list(alphabet.upper()) + list(numbers)) for i in range(length)])
