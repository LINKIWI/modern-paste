import unittest

import config
import constants.build_environment
import util.templating


class TestTemplating(unittest.TestCase):
    def test_import_css(self):
        import_css = util.templating.import_static_resources()['import_css']

        for environment_type in [constants.build_environment.DEV, constants.build_environment.PROD]:
            config.BUILD_ENVIRONMENT = environment_type
            self.assertEqual(
                '<link rel="stylesheet" type="text/css" href="/static/build/path.css">',
                import_css(['path.css'])
            )
            self.assertEqual(
                '<link rel="stylesheet" type="text/css" href="/static/build/path/nested/in/directory.css">',
                import_css(['path/nested/in/directory.css'])
            )
            self.assertEqual(
                '<link rel="stylesheet" type="text/css" href="/static/build/path.css">',
                import_css(['path.css', 'path.css', 'path.css'])
            )
            self.assertEqual(
                '<link rel="stylesheet" type="text/css" href="/static/build/path.css">\n'
                '<link rel="stylesheet" type="text/css" href="/static/build/otherpath.css">',
                import_css(['path.css', 'otherpath.css'])
            )

    def test_import_js(self):
        import_js = util.templating.import_static_resources()['import_js']

        config.BUILD_ENVIRONMENT = constants.build_environment.DEV
        self.assertEqual(
            '<script src="/static/js/path.js" type="text/javascript"></script>',
            import_js(['path.js'])
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
            '<script src="/static/build/js.js" type="text/javascript"></script>',
            import_js(['path.js'])
        )
        self.assertEqual(
            '<script src="/static/build/js.js" type="text/javascript"></script>',
            import_js(['path/nested/in/directory.js'])
        )
        self.assertEqual(
            '<script src="/static/build/js.js" type="text/javascript"></script>',
            import_js(['path.js', 'path.js', 'path.js'])
        )
        self.assertEqual(
            '<script src="/static/build/js.js" type="text/javascript"></script>',
            import_js(['path.js', 'otherpath.js'])
        )
