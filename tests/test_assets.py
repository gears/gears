from gears.assets import CircularDependencyError, Asset, StaticAsset, build_asset
from gears.compat import str, bytes

from .helpers import GearsTestCase


class AssetTests(GearsTestCase):

    fixtures_root = 'assets'

    def test_circular_dependency(self):
        with self.assertRaises(CircularDependencyError):
            asset = self.get_asset('circular_dependency')

    def test_unicode_support(self):
        asset = self.get_asset('unicode_support')
        output = self.get_output('unicode_support')
        self.assertEqual(str(asset), output)

    def test_is_iterable(self):
        asset = self.get_asset('unicode_support')
        tuple(asset)

    def test_is_convertible_to_bytes(self):
        asset = self.get_asset('unicode_support')
        bytes(asset)


class StaticAssetTests(GearsTestCase):

    fixtures_root = 'assets'

    def test_source(self):
        asset = self.get_static_asset('static_source')
        asset.source

    def test_is_iterable(self):
        asset = self.get_static_asset('static_source')
        tuple(asset)

    def test_is_convertible_to_bytes(self):
        asset = self.get_static_asset('static_source')
        bytes(asset)


class BuildAssetTests(GearsTestCase):

    fixtures_root = 'assets'

    def setUp(self):
        self.environment = self.get_environment('build_asset')

    def test_has_processors(self):
        asset = build_asset(self.environment, 'source.js')
        self.assertIsInstance(asset, Asset)

    def test_has_no_processors(self):
        asset = build_asset(self.environment, 'source.md')
        self.assertIsInstance(asset, StaticAsset)
