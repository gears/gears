from gears.assets import (
    CircularDependencyError, BaseAsset, Asset, StaticAsset, build_asset,
    strip_fingerprint
)
from gears.compat import str, bytes

from mock import sentinel, Mock
from unittest2 import TestCase
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

    def test_hexdigest(self):
        asset = self.get_static_asset('static_source')
        self.assertEqual(
            asset.hexdigest,
            'c8a756475599e6e3c904b24077b4b0a31983752c',
        )

    def test_is_iterable(self):
        asset = self.get_static_asset('static_source')
        tuple(asset)

    def test_is_convertible_to_bytes(self):
        asset = self.get_static_asset('static_source')
        bytes(asset)


class HexdigestPathTests(TestCase):

    def get_asset(self, logical_path):
        attributes = Mock(logical_path=logical_path)
        asset = BaseAsset(attributes, sentinel.absolute_path)
        asset.final_hexdigest = '123456'
        return asset

    def test_hexdigest_path(self):
        def check(logical_path, result):
            asset = self.get_asset(logical_path)
            self.assertEqual(asset.hexdigest_path, result)

        check('css/style.css', 'css/style.123456.css')
        check('css/style.min.css', 'css/style.min.123456.css')


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

    def test_strips_fingerprint(self):
        path = 'source.38976434f000bf447d2dc6980894986aaf4e82d0.js'
        asset = build_asset(self.environment, path)
        self.assertEqual(asset.attributes.logical_path, 'source.js')


class StripFingerprintTests(TestCase):

    def test_strips_fingerprint(self):
        path = 'source.38976434f000bf447d2dc6980894986aaf4e82d0.js'
        self.assertEqual(strip_fingerprint(path), 'source.js')

    def test_skips_paths_without_fingerprint(self):
        self.assertEqual(strip_fingerprint('source.js'), 'source.js')
