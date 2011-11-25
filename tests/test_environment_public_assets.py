from gears.environment import PublicAssets
from unittest2 import TestCase


class PublicAssetsTests(TestCase):

    def setUp(self):
        self.public_assets = PublicAssets()

    def test_register_defaults(self):
        self.public_assets.register_defaults()
        self.assertEqual(self.public_assets, ['css/style.css', 'js/script.js'])

    def test_register(self):
        self.public_assets.register('js/app.js')
        self.public_assets.register('js/admin.js')
        self.assertEqual(self.public_assets, ['js/app.js', 'js/admin.js'])

    def test_register_twice(self):
        self.public_assets.register('js/app.js')
        self.public_assets.register('js/app.js')
        self.assertEqual(self.public_assets, ['js/app.js'])

    def test_unregister(self):
        self.public_assets.register('js/app.js')
        self.public_assets.unregister('js/app.js')
        self.assertEqual(self.public_assets, [])

    def test_unregister_if_does_not_exist(self):
        self.public_assets.unregister('js/admin.js')
