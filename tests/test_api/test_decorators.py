import mock
import flask
from flask import request
from flask import render_template
from flask.ext.login import login_user
from flask.ext.login import logout_user

import constants.api
import api.decorators
import util.testing
from api.decorators import hide_if_logged_in
from api.decorators import require_form_args
from api.decorators import require_login_api
from api.decorators import require_login_frontend
from api.decorators import render_view
from modern_paste import app
from uri.main import *


class TestDecorators(util.testing.DatabaseTestCase):
    def test_render_view(self):
        with mock.patch.object(api.decorators, 'render_template') as render_template_mock:
            @render_view
            def template_without_context():
                return 'template name', {}
            template_without_context()
            self.assertEqual(1, render_template_mock.call_count)
            render_template_mock.assert_called_with(
                'template name',
                config=api.decorators.context_config,
            )

        with mock.patch.object(api.decorators, 'render_template') as render_template_mock:
            @render_view
            def template_with_context():
                return 'template name', {'key': 'value'}
            template_with_context()
            self.assertEqual(1, render_template_mock.call_count)
            render_template_mock.assert_called_with(
                'template name',
                config=api.decorators.context_config,
                key='value',
            )

        with mock.patch.object(api.decorators, 'render_template') as render_template_mock:
            @render_view
            def template_with_config_context():
                return 'template name', {'config': {'key': 'value'}}
            template_with_config_context()
            self.assertEqual(1, render_template_mock.call_count)
            expect_config = dict(api.decorators.context_config)
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

    def test_require_login_api(self):
        with app.test_request_context():
            @require_login_api
            def login_required():
                return 'success'
            self.assertEqual(login_required()[1], constants.api.AUTH_FAILURE_CODE)
            user = util.testing.UserFactory.generate(password='password')
            request.get_json = lambda: {
                'username': user.user_id,
                'password': 'password',
            }
            login_user(user)
            self.assertEqual(login_required(), 'success')

            def login_not_required():
                return 'success'
            self.assertEqual(login_not_required(), 'success')
            logout_user()
            self.assertEqual(login_not_required(), 'success')

    def test_require_login_frontend(self):
        with app.test_request_context():
            @require_login_frontend
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
