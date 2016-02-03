import unittest

import config
import constants.build_environment
import util.cryptography
import util.templating
from uri.paste import PasteSubmitURI


class TestTemplating(unittest.TestCase):
    def test_import_css(self):
        import_css = util.templating.import_static_resources()['import_css']

        for environment_type in [constants.build_environment.DEV, constants.build_environment.PROD]:
            config.BUILD_ENVIRONMENT = environment_type
            self.assertEqual(
                '<link rel="stylesheet" type="text/css" href="//external_resource.css">',
                import_css(['//external_resource.css'])
            )
            self.assertEqual(
                '<link rel="stylesheet" type="text/css" href="/static/build/css/path.css">',
                import_css(['path.css'])
            )
            self.assertEqual(
                '<link rel="stylesheet" type="text/css" href="/static/lib/path.css">',
                import_css(['lib/path.css'])
            )
            self.assertEqual(
                '<link rel="stylesheet" type="text/css" href="/static/lib/path.css">',
                import_css(['lib/path.css'])
            )
            self.assertEqual(
                '<link rel="stylesheet" type="text/css" href="/static/build/css/path/nested/in/directory.css">',
                import_css(['path/nested/in/directory.css'])
            )
            self.assertEqual(
                '<link rel="stylesheet" type="text/css" href="/static/build/css/path.css">',
                import_css(['path.css', 'path.css', 'path.css'])
            )
            self.assertEqual(
                '<link rel="stylesheet" type="text/css" href="/static/build/css/path.css">\n'
                '<link rel="stylesheet" type="text/css" href="/static/build/css/otherpath.css">',
                import_css(['path.css', 'otherpath.css'])
            )

    def test_import_js(self):
        import_js = util.templating.import_static_resources()['import_js']

        config.BUILD_ENVIRONMENT = constants.build_environment.DEV
        self.assertEqual(
            '<script src="//external_resource.js" type="text/javascript"></script>',
            import_js(['//external_resource.js'])
        )
        self.assertEqual(
            '<script src="/static/lib/lib.js" type="text/javascript"></script>',
            import_js(['lib/lib.js'])
        )
        self.assertEqual(
            '<script src="/static/js/path.js" type="text/javascript"></script>',
            import_js(['path.js'])
        )
        self.assertEqual(
            '<script src="/static/js/path.js" type="text/javascript" defer></script>',
            import_js(['path.js'], defer=True)
        )
        self.assertEqual(
            '<script src="/static/js/path/nested/in/directory.js" type="text/javascript"></script>',
            import_js(['path/nested/in/directory.js'])
        )
        self.assertEqual(
            '<script src="/static/js/path.js" type="text/javascript"></script>',
            import_js(['path.js', 'path.js', 'path.js'])
        )
        self.assertEqual(
            '<script src="/static/js/path.js" type="text/javascript"></script>\n'
            '<script src="/static/js/otherpath.js" type="text/javascript"></script>',
            import_js(['path.js', 'otherpath.js'])
        )

        config.BUILD_ENVIRONMENT = constants.build_environment.PROD
        self.assertEqual(
            '<script src="//external_resource.js" type="text/javascript"></script>',
            import_js(['//external_resource.js'])
        )
        self.assertEqual(
            '<script src="/static/lib/lib.js" type="text/javascript"></script>',
            import_js(['lib/lib.js'])
        )
        self.assertEqual(
            '<script src="/static/lib/lib.js" type="text/javascript" defer></script>',
            import_js(['lib/lib.js'], defer=True)
        )
        self.assertEqual(
            '',
            import_js(['universal/js.js'])
        )
        self.assertEqual(
            '<script src="/static/build/js/path.js" type="text/javascript"></script>',
            import_js(['path.js'])
        )
        self.assertEqual(
            '<script src="/static/build/js/path/nested/in/directory.js" type="text/javascript"></script>',
            import_js(['path/nested/in/directory.js'])
        )
        self.assertEqual(
            '<script src="/static/build/js/path.js" type="text/javascript"></script>',
            import_js(['path.js', 'path.js', 'path.js'])
        )
        self.assertEqual(
            '<script src="/static/build/js/path.js" type="text/javascript"></script>\n'
            '<script src="/static/build/js/otherpath.js" type="text/javascript"></script>',
            import_js(['path.js', 'otherpath.js'])
        )
        self.assertEqual(
            '<script src="/static/build/js/multipart/ControllerController.js" type="text/javascript"></script>',
            import_js(['multipart/controller/MainController.js', 'multipart/controller/MainSubController.js'])
        )

    def test_get_uri_path(self):
        uri = util.templating.get_uri_path()['uri']
        full_uri = util.templating.get_uri_path()['full_uri']

        self.assertEqual(PasteSubmitURI.uri(), uri('paste', 'PasteSubmitURI'))
        self.assertEqual(PasteSubmitURI.uri(key='value'), uri('paste', 'PasteSubmitURI', key='value'))
        self.assertEqual(PasteSubmitURI.full_uri(), full_uri('paste', 'PasteSubmitURI'))
        self.assertEqual(PasteSubmitURI.full_uri(key='value'), full_uri('paste', 'PasteSubmitURI', key='value'))

    def test_get_id_repr(self):
        id_repr = util.templating.get_id_repr()['id_repr']

        decid = 25
        encid = util.cryptography.get_encid(decid)

        config.USE_ENCRYPTED_IDS = True
        self.assertEqual(encid, id_repr(decid))
        self.assertEqual(encid, id_repr(encid))

        config.USE_ENCRYPTED_IDS = False
        self.assertEqual(decid, id_repr(decid))
        self.assertEqual(decid, id_repr(encid))

    def test_get_all_uris(self):
        uri = util.templating.get_uri_path()['uri']
        all_uris = util.templating.get_all_uris()['all_uris']()
        self.assertGreater(len(all_uris), 0)

        for uri_module in all_uris:
            for uri_class in all_uris[uri_module]:
                self.assertIsNotNone(uri(uri_module, uri_class))
