import unittest

import config
from uri.base_uri import URI


class TestURI(URI):
    fqdn = 'domain.com'
    path = '/test-uri-path'


class TestEmbeddedParamsURI(URI):
    fqdn = 'domain.com'
    path = '/test/<embed>/uri'


class TestBaseURI(unittest.TestCase):
    def test_uri(self):
        self.assertEqual('/test-uri-path', TestURI.uri())
        self.assertEqual('/test-uri-path?key1=value1', TestURI.uri(key1='value1'))
        self.assertEqual('/test-uri-path?key2=value2&key1=value1', TestURI.uri(key1='value1', key2='value2'))

        self.assertEqual('/test/key/uri', TestEmbeddedParamsURI.uri(embed='key'))
        self.assertEqual('/test/key/uri?extra=param', TestEmbeddedParamsURI.uri(embed='key', extra='param'))

    def test_full_uri(self):
        config.DEFAULT_HTTPS = False
        self.assertEqual('http://domain.com/test-uri-path', TestURI.full_uri())
        self.assertEqual('https://domain.com/test-uri-path', TestURI.full_uri(https=True))
        self.assertEqual('http://domain.com/test-uri-path?key1=value1', TestURI.full_uri(key1='value1'))
        self.assertEqual('https://domain.com/test-uri-path?key1=value1', TestURI.full_uri(key1='value1', https=True))
        self.assertEqual('http://domain.com/test-uri-path?key2=value2&key1=value1', TestURI.full_uri(key1='value1', key2='value2'))
        self.assertEqual('http://domain.com/test/key/uri', TestEmbeddedParamsURI.full_uri(embed='key'))
        self.assertEqual('http://domain.com/test/key/uri?extra=param', TestEmbeddedParamsURI.full_uri(embed='key', extra='param'))

        config.DEFAULT_HTTPS = True
        self.assertEqual('https://domain.com/test-uri-path', TestURI.full_uri())
        self.assertEqual('https://domain.com/test-uri-path?key1=value1', TestURI.full_uri(key1='value1'))
        self.assertEqual('https://domain.com/test-uri-path?key2=value2&key1=value1', TestURI.full_uri(key1='value1', key2='value2'))

    def test_get_path(self):
        self.assertEqual('/test-uri-path', TestURI.get_path())

    def test_protocol_prefix(self):
        self.assertEqual('http://', TestURI.protocol_prefix(https=False))
        self.assertEqual('https://', TestURI.protocol_prefix(https=True))
