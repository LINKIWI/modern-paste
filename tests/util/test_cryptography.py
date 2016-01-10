import unittest

import config
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

    def test_get_id_repr(self):
        decid = 25
        encid = util.cryptography.get_encid(decid)

        config.USE_ENCRYPTED_IDS = True
        self.assertEqual(encid, util.cryptography.get_id_repr(decid))
        self.assertEqual(encid, util.cryptography.get_id_repr(encid))

        config.USE_ENCRYPTED_IDS = False
        self.assertEqual(decid, util.cryptography.get_id_repr(decid))
        self.assertEqual(decid, util.cryptography.get_id_repr(encid))

    def test_secure_hash(self):
        # Given the same number of iterations (10000), this result should always be the same
        self.assertEqual(
            'c1d1fad8cd48495c6999c8677a50641845af5b5ae848d4c4616d78e81e6454c8',
            util.cryptography.secure_hash('test string'),
        )
        # Final hash should *not* be the result of only hashing the input once
        self.assertNotEqual(
            'd5579c46dfcc7f18207013e65b44e4cb4e2c2298f4ac457ba8f82743f31e930b',
            util.cryptography.secure_hash('test string'),
        )
