import util.testing
import views.error
import views.paste


class TestError(util.testing.DatabaseTestCase):
    def test_not_found(self):
        self.assertIn('404 NOT FOUND', views.error.not_found(None))
        self.assertIn('404 NOT FOUND', self.client.get('/invalid').data)

    def test_internal_server_error(self):
        self.assertIn('500 INTERNAL SERVER ERROR', views.error.internal_server_error(None))
