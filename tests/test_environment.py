import os
import shutil
import sys
from contextlib import contextmanager

from gears.asset_attributes import AssetAttributes
from gears.compat import str
from gears.environment import Environment
from gears.exceptions import FileNotFound
from gears.finders import FileSystemFinder

from mock import Mock
from unittest2 import TestCase


ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'assets'))
STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))


class FakeCompiler(object):

    def __init__(self, result_mimetype):
        self.result_mimetype = result_mimetype


class FakeFinder(object):

    paths = (
        'js/script.js',
        'js/app/index.js',
        'js/models.js.coffee',
        'images/logo.png',
    )

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
        self.environment.compilers.register('.styl', FakeCompiler('text/css'))
        self.assertItemsEqual(self.environment.suffixes.find(), [
            '.css', '.styl', '.css.styl', '.txt',
        ])

    def test_register_defaults(self):
        self.environment.mimetypes = Mock()
        self.environment.preprocessors = Mock()
        self.environment.register_defaults()
        self.environment.mimetypes.register_defaults.assert_called_once_with()
        self.environment.preprocessors.register_defaults.assert_called_once_with()


class EnvironmentFindTests(TestCase):

    def setUp(self):
        self.environment = Environment(STATIC_DIR)
        self.environment.register_defaults()
        self.environment.finders.register(FakeFinder())
        self.environment.compilers.register(
            '.coffee', FakeCompiler('application/javascript'))

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

    def test_find_by_logical_path_with_unrecognized_extension(self):
        attrs, path = self.environment.find('images/logo.png', logical=True)
        self.check_asset_attributes(attrs, 'images/logo.png')
        self.assertEqual(path, '/assets/images/logo.png')

    def test_find_nothing_by_logical_path(self):
        with self.assertRaises(FileNotFound):
            self.environment.find('js/views.js', logical=True)

    def test_save_file(self):
        source = str('hello world').encode('utf-8')
        with remove_static_dir():
            self.environment.save_file('js/script.js', source)
            with open(os.path.join(STATIC_DIR, 'js', 'script.js'), 'rb') as f:
                self.assertEqual(f.read(), source)


class EnvironmentListTests(TestCase):

    def setUp(self):
        self.environment = Environment(STATIC_DIR)
        self.environment.register_defaults()
        self.environment.finders.register(FileSystemFinder([ASSETS_DIR]))

    def test_list(self):
        items = list(self.environment.list('js/templates/*', 'application/javascript'))
        self.assertEqual(len(items), 3)
        for i, item in enumerate(sorted(items, key=lambda x: x[1])):
            path = 'js/templates/%s.js.handlebars' % 'abc'[i]
            asset_attributes, absolute_path = item
            self.assertIsInstance(asset_attributes, AssetAttributes)
            self.assertEqual(asset_attributes.path, path)
            self.assertEqual(absolute_path, os.path.join(ASSETS_DIR, path))

    def test_list_recursively(self):
        items = list(self.environment.list('js/templates/**', 'application/javascript'))
        self.assertEqual(len(items), 4)
        for i, item in enumerate(sorted(items, key=lambda x: x[1])):
            path = 'js/templates/%s.js.handlebars' % ('a', 'b', 'c', 'd/e')[i]
            asset_attributes, absolute_path = item
            self.assertIsInstance(asset_attributes, AssetAttributes)
            self.assertEqual(asset_attributes.path, path)
            self.assertEqual(absolute_path, os.path.join(ASSETS_DIR, path))
