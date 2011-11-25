from gears.environment import Suffixes
from unittest2 import TestCase


class SuffixesTests(TestCase):

    def setUp(self):
        self.suffixes = Suffixes()

    def test_register_root_extensions(self):
        self.suffixes.register('.css', root=True, mimetype='text/css')
        self.suffixes.register('.txt', root=True, mimetype='text/plain')
        self.assertEqual(
            self.suffixes,
            [{'extensions': ['.css'], 'mimetype': 'text/css'},
             {'extensions': ['.txt'], 'mimetype': 'text/plain'}])

    def test_register_extension_to_mimetype(self):
        self.suffixes.register('.css', root=True, mimetype='text/css')
        self.suffixes.register('.txt', root=True, mimetype='text/plain')
        self.suffixes.register('.styl', to='text/css')
        self.assertEqual(
            self.suffixes,
            [{'extensions': ['.css'], 'mimetype': 'text/css'},
             {'extensions': ['.txt'], 'mimetype': 'text/plain'},
             {'extensions': ['.css', '.styl'], 'mimetype': None}])

    def test_register_extension_to_none(self):
        self.suffixes.register('.css', root=True, mimetype='text/css')
        self.suffixes.register('.txt', root=True, mimetype='text/plain')
        self.suffixes.register('.styl', to='text/css')
        self.suffixes.register('.tmpl')
        self.assertEqual(
            self.suffixes,
            [{'extensions': ['.css'], 'mimetype': 'text/css'},
             {'extensions': ['.txt'], 'mimetype': 'text/plain'},
             {'extensions': ['.css', '.styl'], 'mimetype': None},
             {'extensions': ['.css', '.tmpl'], 'mimetype': None},
             {'extensions': ['.txt', '.tmpl'], 'mimetype': None},
             {'extensions': ['.css', '.styl', '.tmpl'], 'mimetype': None}])

    def test_unregister_extension(self):
        self.suffixes.register('.css', root=True, mimetype='text/css')
        self.suffixes.register('.txt', root=True, mimetype='text/plain')
        self.suffixes.register('.styl', to='text/css')
        self.suffixes.register('.tmpl')
        self.suffixes.unregister('.css')
        self.assertEqual(
            self.suffixes,
            [{'extensions': ['.txt'], 'mimetype': 'text/plain'},
             {'extensions': ['.txt', '.tmpl'], 'mimetype': None}])

    def test_find_all(self):
        self.suffixes.register('.css', root=True, mimetype='text/css')
        self.suffixes.register('.txt', root=True, mimetype='text/plain')
        self.suffixes.register('.styl', to='text/css')
        self.assertEqual(self.suffixes.find(), ['.css', '.txt', '.css.styl'])

    def test_find_by_extension(self):
        self.suffixes.register('.css', root=True, mimetype='text/css')
        self.suffixes.register('.txt', root=True, mimetype='text/plain')
        self.suffixes.register('.styl', to='text/css')
        self.assertEqual(self.suffixes.find('.css'), ['.css', '.css.styl'])

    def test_find_by_many_extensions(self):
        self.suffixes.register('.css', root=True, mimetype='text/css')
        self.suffixes.register('.txt', root=True, mimetype='text/plain')
        self.suffixes.register('.styl', to='text/css')
        self.assertEqual(self.suffixes.find('.css', '.styl'), ['.css.styl'])

    def test_find_nothing(self):
        self.assertEqual(self.suffixes.find('.css'), [])
