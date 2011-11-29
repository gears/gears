from __future__ import with_statement

import os
import shutil
from contextlib import contextmanager

from gears.asset_attributes import AssetAttributes
from gears.environment import Environment
from gears.exceptions import FileNotFound

from mock import Mock
from unittest2 import TestCase


STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))


class FakeEngine(object):

    def __init__(self, result_mimetype):
        self.result_mimetype = result_mimetype


class FakeFinder(object):

    paths = ('js/script.js', 'js/app/index.js', 'js/models.js.coffee')

    def find(self, path):
        if path in self.paths:
            return '/assets/' + path
        raise FileNotFound(path)


@contextmanager
def remove_static_dir():
    if os.path.exists(STATIC_DIR):
        shutil.rmtree(STATIC_DIR)
    yield
    if os.path.exists(STATIC_DIR):
        shutil.rmtree(STATIC_DIR)


class EnvironmentTests(TestCase):

    def setUp(self):
        self.environment = Environment(STATIC_DIR)

    def test_suffixes(self):
        self.environment.mimetypes.register('.css', 'text/css')
        self.environment.mimetypes.register('.txt', 'text/plain')
        self.environment.engines.register('.styl', FakeEngine('text/css'))
        self.assertItemsEqual(self.environment.suffixes.find(),
                              ['.css', '.css.styl', '.txt'])

    def test_register_defaults(self):
        self.environment.engines = Mock()
        self.environment.mimetypes = Mock()
        self.environment.public_assets = Mock()
        self.environment.preprocessors = Mock()
        self.environment.register_defaults()
        self.environment.engines.register_defaults.assert_called_once_with()
        self.environment.mimetypes.register_defaults.assert_called_once_with()
        self.environment.public_assets.register_defaults.assert_called_once_with()
        self.environment.preprocessors.register_defaults.assert_called_once_with()


class EnvironmentFindTests(TestCase):

    def setUp(self):
        self.environment = Environment(STATIC_DIR)
        self.environment.register_defaults()
        self.environment.finders.register(FakeFinder())
        self.environment.engines.register(
            '.coffee', FakeEngine('application/javascript'))

    def check_asset_attributes(self, attrs, path):
        self.assertIsInstance(attrs, AssetAttributes)
        self.assertIs(attrs.environment, self.environment)
        self.assertEqual(attrs.path, path)

    def test_find_by_path(self):
        attrs, path = self.environment.find('js/models.js.coffee')
        self.check_asset_attributes(attrs, 'js/models.js.coffee')
        self.assertEqual(path, '/assets/js/models.js.coffee')

    def test_find_nothing_by_path(self):
        with self.assertRaises(FileNotFound):
            self.environment.find('js/models.js')

    def test_find_by_path_list(self):
        attrs, path = self.environment.find(['js/app.js', 'js/app/index.js'])
        self.check_asset_attributes(attrs, 'js/app/index.js')
        self.assertEqual(path, '/assets/js/app/index.js')

    def test_find_nothing_by_path_list(self):
        with self.assertRaises(FileNotFound):
            self.environment.find(['style.css', 'style/index.css'])

    def test_find_by_asset_attributes(self):
        attrs = AssetAttributes(self.environment, 'js/app.js')
        attrs, path = self.environment.find(attrs)
        self.check_asset_attributes(attrs, 'js/app/index.js')
        self.assertEqual(path, '/assets/js/app/index.js')

    def test_find_nothing_by_asset_attributes(self):
        attrs = AssetAttributes(self.environment, 'js/models.js')
        with self.assertRaises(FileNotFound):
            self.environment.find(attrs)

    def test_find_by_logical_path(self):
        attrs, path = self.environment.find('js/models.js', logical=True)
        self.check_asset_attributes(attrs, 'js/models.js.coffee')
        self.assertEqual(path, '/assets/js/models.js.coffee')

    def test_find_nothing_by_logical_path(self):
        with self.assertRaises(FileNotFound):
            self.environment.find('js/views.js', logical=True)

    def test_save_file(self):
        with remove_static_dir():
            self.environment.save_file('js/script.js', 'hello world')
            with open(os.path.join(STATIC_DIR, 'js', 'script.js')) as f:
                self.assertEqual(f.read(), 'hello world')
