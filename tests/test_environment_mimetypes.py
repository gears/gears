from gears.environment import MIMETypes
from unittest2 import TestCase


class MIMETypesTests(TestCase):

    def setUp(self):
        self.mimetypes = MIMETypes()
        self.mimetypes.register_defaults()

    def test_register(self):
        self.mimetypes.register('.txt', 'text/plain')
        self.assertIn('.txt', self.mimetypes)
        self.assertEqual(self.mimetypes['.txt'], 'text/plain')

    def test_unregister(self):
        self.assertIn('.css', self.mimetypes)
        self.mimetypes.unregister('.css')
        self.assertNotIn('.css', self.mimetypes)

    def test_get_if_exists(self):
        self.assertEqual(self.mimetypes.get('.css'), 'text/css')

    def test_get_if_does_not_exist(self):
        self.assertIsNone(self.mimetypes.get('.txt'))
