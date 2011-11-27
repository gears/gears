from __future__ import with_statement

import os

from gears.asset_attributes import AssetAttributes
from gears.assets import (
    BaseAsset, Asset, StaticAsset, AssetAlreadyUsed, build_asset)
from gears.environment import Environment

from mock import Mock, patch
from unittest2 import TestCase


ASSETS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'assets')


class BaseAssetTests(TestCase):

    def create_asset(self, path, context=None, calls=None):
        attributes = AssetAttributes(Environment('static'), path)
        return BaseAsset(attributes, '/assets/' + path, context, calls)

    def test_if_asset_added_to_calls(self):
        calls = set()
        self.create_asset('js/script.js', calls=calls)
        self.assertIn('/assets/js/script.js', calls)

    def test_if_asset_already_used(self):
        calls = set(['/assets/js/script.js'])
        with self.assertRaises(AssetAlreadyUsed):
            self.create_asset('js/script.js', calls=calls)

    def test_str(self):
        asset = self.create_asset('js/script.js')
        asset.get_source = Mock(return_value='base_asset')
        self.assertEqual(str(asset), 'base_asset')
        self.assertEqual(asset.get_source.call_count, 1)


class AssetTests(TestCase):

    def create_asset(self, path, context=None, calls=None):
        attributes = AssetAttributes(Environment('static'), path)
        absolute_path = os.path.join(ASSETS_DIR, path)
        return Asset(attributes, absolute_path, context, calls)

    @patch.object(AssetAttributes, 'path_without_extensions')
    def test_get_context(self, path_without_extensions):
        context = self.create_asset('js/script.js').get_context()
        self.assertEqual(context, {'name': path_without_extensions})

    def test_get_source(self):
        asset = self.create_asset('js/script.js')
        asset.get_context = Mock()
        processors = [Mock(), Mock(), Mock()]
        with patch.object(AssetAttributes, 'processors', processors):
            source = asset.get_source()
            processors[0].process.assert_called_once_with(
                "console.log('hello world');\n",
                asset.get_context.return_value, asset.calls)
            processors[1].process.assert_called_once_with(
                processors[0].process.return_value,
                asset.get_context.return_value, asset.calls)
            processors[2].process.assert_called_once_with(
                processors[1].process.return_value,
                asset.get_context.return_value, asset.calls)
            self.assertEqual(source, processors[2].process.return_value)


class StaticAssetTests(TestCase):

    def create_asset(self, path, context=None, calls=None):
        attributes = AssetAttributes(Environment('static'), path)
        absolute_path = os.path.join(ASSETS_DIR, path)
        return StaticAsset(attributes, absolute_path, context, calls)

    def test_process(self):
        asset = self.create_asset('js/script.js')
        self.assertEqual(asset.get_source(), "console.log('hello world');\n")


class BuildAssetTests(TestCase):

    def setUp(self):
        self.environment = Environment('static')
        self.environment.public_assets.register('js/script.js')

    def test_if_asset_has_processors(self):
        asset_attributes = Mock()
        asset_attributes.processors = True
        absolute_path = '/assets/js/script.js'
        self.environment.find = Mock(
            return_value=(asset_attributes, absolute_path))

        asset = build_asset(self.environment, 'js/script.js')
        self.assertIsInstance(asset, Asset)
        self.assertIs(asset.attributes, asset_attributes)
        self.assertEqual(asset.absolute_path, absolute_path)

    def test_if_asset_has_no_processors(self):
        asset_attributes = Mock()
        asset_attributes.processors = False
        absolute_path = '/assets/js/script.js'
        self.environment.find = Mock(
            return_value=(asset_attributes, absolute_path))

        asset = build_asset(self.environment, 'js/script.js')
        self.assertIsInstance(asset, StaticAsset)
        self.assertIs(asset.attributes, asset_attributes)
        self.assertEqual(asset.absolute_path, absolute_path)

    def test_if_asset_does_not_exist(self):
        self.environment.find = Mock(return_value=(None, None))
        self.assertIsNone(build_asset(self.environment, 'js/script.js'))

    def test_if_asset_is_not_public(self):
        self.assertIsNone(build_asset(self.environment, 'js/app.js'))
