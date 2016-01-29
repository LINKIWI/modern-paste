import mock
import json
import os

import util.cryptography
import util.testing

import views.misc
import constants.api
import constants.build_environment


class TestMisc(util.testing.DatabaseTestCase):
    @mock.patch('config.BUILD_ENVIRONMENT', constants.build_environment.DEV)
    def test_dev_banner_dev(self):
        # Not specific to API documentation page.
        self.assertIn('dev-banner', views.misc.api_documentation_interface())

    @mock.patch('config.BUILD_ENVIRONMENT', constants.build_environment.PROD)
    def test_dev_banner_prod(self):
        self.assertNotIn('dev-banner', views.misc.api_documentation_interface())

    def test_api_documentation_interface(self):
        api_documentation = views.misc.api_documentation_interface()

        # All generic error responses should be documented
        for response_name in filter(lambda constant: constant.endswith('_FAILURE'), dir(constants.api)):
            self.assertIn(
                getattr(constants.api, response_name)[constants.api.FAILURE],
                api_documentation,
                'Failure JSON API constant {response} added, but no corresponding documentation exists '
                'in templates/api_documentation.json'.format(response=response_name),
            )

        # All API endpoints in the JSON data should be rendered in the template
        documented_api_endpoints = json.loads(
            open(os.path.realpath('app/templates/misc/api_documentation.json')).read()
        )['api_endpoints']
        for endpoint in documented_api_endpoints:
            self.assertIn(endpoint['name'].replace(' ', '-').lower(), api_documentation)
