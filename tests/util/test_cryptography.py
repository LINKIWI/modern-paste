import unittest

import util.cryptography
from util.exception import *


class TestCryptography(unittest.TestCase):
    def test_get_encid(self):
        self.assertRaises(
            InvalidIDException,
            util.cryptography.get_encid,
            [],
        )

        encid = util.cryptography.get_encid(15)
        self.assertEqual(len(encid), 44)
        self.assertNotIn('/', list(encid))
        self.assertNotIn('\\', list(encid))

    def test_get_decid(self):
        self.assertRaises(
            InvalidIDException,
            util.cryptography.get_decid,
            [],
        )
        self.assertRaises(
            InvalidIDException,
            util.cryptography.get_decid,
            'invalid',
        )

        encid = util.cryptography.get_encid(15)
        decid = util.cryptography.get_decid(encid)
        self.assertEqual(decid, 15)
