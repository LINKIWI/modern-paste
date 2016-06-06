import json

import mock
from flask import request
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user

import config
import api.decorators
import constants.api
import database.user
import util.testing
from api.decorators import hide_if_logged_in
from api.decorators import optional_login_api
from api.decorators import render_view
from api.decorators import require_form_args
from api.decorators import require_login_api
from api.decorators import require_login_frontend
from modern_paste import app
from uri.main import *


class TestDecorators(util.testing.DatabaseTestCase):
    def test_context_config(self):
        config_constants = api.decorators.context_config()
        for config_item in filter(lambda item: item == item.upper(), dir(config)):
            self.assertIn(config_item, config_constants)

    def test_render_view(self):
        with mock.patch.object(api.decorators, 'render_template') as render_template_mock:
            @render_view
            def template_without_context():
                return 'template name', {}
            template_without_context()
            self.assertEqual(1, render_template_mock.call_count)
            render_template_mock.assert_called_with(
                'template name',
                config=api.decorators.context_config(),
            )

        with mock.patch.object(api.decorators, 'render_template') as render_template_mock:
            @render_view
            def template_with_context():
                return 'template name', {'key': 'value'}
            template_with_context()
            self.assertEqual(1, render_template_mock.call_count)
            render_template_mock.assert_called_with(
                'template name',
                config=api.decorators.context_config(),
                key='value',
            )

        with mock.patch.object(api.decorators, 'render_template') as render_template_mock:
            @render_view
            def template_with_config_context():
                return 'template name', {'config': {'key': 'value'}}
            template_with_config_context()
            self.assertEqual(1, render_template_mock.call_count)
            expect_config = dict(api.decorators.context_config())
            expect_config['key'] = 'value'
            render_template_mock.assert_called_with(
                'template name',
                config=expect_config,
            )

    def test_require_form_args(self):
        with app.test_request_context():
            @require_form_args([])
            def no_required_args():
                return 'success'
            request.get_json = lambda: {}
            self.assertEqual(no_required_args(), 'success')
            request.get_json = lambda: {'extraneous': 'content'}
            self.assertEqual(no_required_args(), 'success')

            @require_form_args(['param'])
            def one_required_arg():
                return 'success'
            request.get_json = lambda: {}
            self.assertEqual(one_required_arg()[1], constants.api.INCOMPLETE_PARAMS_FAILURE_CODE)
            request.get_json = lambda: {'invalid': 'invalid'}
            self.assertEqual(one_required_arg()[1], constants.api.INCOMPLETE_PARAMS_FAILURE_CODE)
            request.get_json = lambda: {'param': ''}  # Should reject empty contents
            self.assertEqual(one_required_arg()[1], constants.api.INCOMPLETE_PARAMS_FAILURE_CODE)
            request.get_json = lambda: {'param': 'content'}
            self.assertEqual(one_required_arg(), 'success')

            @require_form_args(['param1', 'param2'])
            def two_required_args():
                return 'success'
            request.get_json = lambda: {}
            self.assertEqual(two_required_args()[1], constants.api.INCOMPLETE_PARAMS_FAILURE_CODE)
            request.get_json = lambda: {'invalid': 'invalid'}
            self.assertEqual(two_required_args()[1], constants.api.INCOMPLETE_PARAMS_FAILURE_CODE)
            request.get_json = lambda: {'param1': 'content'}
            self.assertEqual(two_required_args()[1], constants.api.INCOMPLETE_PARAMS_FAILURE_CODE)
            request.get_json = lambda: {'param1': 'content', 'param2': 'content'}
            self.assertEqual(two_required_args(), 'success')

            @require_form_args(['param'], allow_blank_values=True)
            def blank_values_allowed():
                return 'success'
            request.get_json = lambda: {}
            self.assertEqual(blank_values_allowed()[1], constants.api.INCOMPLETE_PARAMS_FAILURE_CODE)
            request.get_json = lambda: {'invalid': 'invalid'}
            self.assertEqual(blank_values_allowed()[1], constants.api.INCOMPLETE_PARAMS_FAILURE_CODE)
            request.get_json = lambda: {'param': ''}
            self.assertEqual(blank_values_allowed(), 'success')
            request.get_json = lambda: {'param': 'content'}
            self.assertEqual(blank_values_allowed(), 'success')

            @require_form_args(['param'], strict_params=True)
            def strict_params_enforced():
                return 'success'
            request.get_json = lambda: {}
            self.assertEqual(strict_params_enforced()[1], constants.api.INCOMPLETE_PARAMS_FAILURE_CODE)
            request.get_json = lambda: {'invalid': 'invalid'}
            self.assertEqual(strict_params_enforced()[1], constants.api.INCOMPLETE_PARAMS_FAILURE_CODE)
            request.get_json = lambda: {'param': 'content', 'extraneous': 'content'}
            self.assertEqual(strict_params_enforced()[1], constants.api.INCOMPLETE_PARAMS_FAILURE_CODE)
            request.get_json = lambda: {'param': 'content'}
            self.assertEqual(strict_params_enforced(), 'success')

    def test_require_login_api_credentials(self):
        with app.test_request_context():
            @require_login_api
            def login_required():
                return 'success'
            self.assertEqual(login_required()[1], constants.api.AUTH_FAILURE_CODE)
            user = util.testing.UserFactory.generate(password='password')
            login_user(user)
            self.assertEqual(login_required(), 'success')

            def login_not_required():
                return 'success'
            self.assertEqual(login_not_required(), 'success')
            logout_user()
            self.assertEqual(login_not_required(), 'success')

    def test_require_login_api_key(self):
        with app.test_request_context():
            @require_login_api
            def login_required():
                return 'success'
            self.assertEqual(login_required()[1], constants.api.AUTH_FAILURE_CODE)
            user = util.testing.UserFactory.generate(password='password')
            request.get_json = lambda: {
                'api_key': user.api_key,
            }
            self.assertEqual(login_required(), 'success')

    def test_optional_login_api_key(self):
        with app.test_request_context():
            @optional_login_api
            def login_optional():
                if current_user.is_authenticated:
                    return 'authenticated'
                return 'not authenticated'
            self.assertEqual('not authenticated', login_optional())
            user = util.testing.UserFactory.generate(password='password')
            request.get_json = lambda: {
                'api_key': user.api_key,
            }
            self.assertEqual('authenticated', login_optional())

    def test_optional_login_api_credentials(self):
        with app.test_request_context():
            @optional_login_api
            def login_optional():
                if current_user.is_authenticated:
                    return 'authenticated'
                return 'not authenticated'
            self.assertEqual('not authenticated', login_optional())
            user = util.testing.UserFactory.generate(password='password')
            login_user(user)
            self.assertEqual('authenticated', login_optional())

    def test_optional_login_api_invalid_credentials(self):
        with app.test_request_context():
            @optional_login_api
            def login_optional():
                if current_user.is_authenticated:
                    return 'authenticated'
                return 'not authenticated'
            self.assertEqual('not authenticated', login_optional())
            request.get_json = lambda: {
                'api_key': 'invalid',
            }
            resp, resp_code = login_optional()
            self.assertEqual(constants.api.AUTH_FAILURE, json.loads(resp.data))
            self.assertEqual(constants.api.AUTH_FAILURE_CODE, resp_code)

    def test_optional_login_api_deactivated_user(self):
        with app.test_request_context():
            @optional_login_api
            def login_optional():
                if current_user.is_authenticated:
                    return 'authenticated'
                return 'not authenticated'
            self.assertEqual('not authenticated', login_optional())
            user = util.testing.UserFactory.generate()
            database.user.deactivate_user(user.user_id)
            request.get_json = lambda: {
                'api_key': user.api_key,
            }
            resp, resp_code = login_optional()
            self.assertEqual(constants.api.AUTH_FAILURE, json.loads(resp.data))
            self.assertEqual(constants.api.AUTH_FAILURE_CODE, resp_code)

    def test_require_login_frontend(self):
        with app.test_request_context():
            @require_login_frontend()
            def login_required():
                return 'success'
            self.assertEqual(login_required().status_code, 302)  # Redirect
            user = util.testing.UserFactory.generate(password='password')
            request.get_json = lambda: {
                'username': user.user_id,
                'password': 'password',
            }
            login_user(user)
            self.assertEqual(login_required(), 'success')

            @require_login_frontend(only_if=False)
            def conditional_login_required():
                return 'success'
            self.assertEqual(login_required(), 'success')

    def test_hide_if_logged_in(self):
        with app.test_request_context():
            @hide_if_logged_in(redirect_uri=HomeURI.uri())
            def hidden_if_logged_in():
                return 'success'
            self.assertEqual(hidden_if_logged_in(), 'success')  # Redirect
            user = util.testing.UserFactory.generate(password='password')
            request.get_json = lambda: {
                'username': user.user_id,
                'password': 'password',
            }
            login_user(user)
            self.assertEqual(hidden_if_logged_in().status_code, 302)
