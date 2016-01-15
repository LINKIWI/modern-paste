import util.testing
import views.paste


class TestPaste(util.testing.DatabaseTestCase):
    def test_paste_post(self):
        self.assertIsNotNone(views.paste.paste_post())

    def test_paste_view(self):
        self.assertIn('PASTE NOT FOUND', views.paste.paste_view(-1))

        paste = util.testing.PasteFactory.generate()
        self.assertIn(str(paste.paste_id), views.paste.paste_view(paste.paste_id))
        self.assertIn(paste.language, views.paste.paste_view(paste.paste_id))
