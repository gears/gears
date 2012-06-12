from gears.environment import Suffixes
from unittest2 import TestCase


class SuffixesTests(TestCase):

    def setUp(self):
        self.suffixes = Suffixes()
        self.suffixes.register('.css', root=True, mimetype='text/css')
        self.suffixes.register('.txt', root=True, mimetype='text/plain')

    def test_register_root_suffix(self):
        self.assertItemsEqual(self.suffixes, [{
            'suffix': ['.css'],
            'result_mimetype': 'text/css',
            'mimetype': 'text/css',
        }, {
            'suffix': ['.txt'],
            'result_mimetype': 'text/plain',
            'mimetype': 'text/plain',
        }])

    def test_register_extension_to_mimetype(self):
        self.suffixes.register('.styl', to='text/css')
        self.assertItemsEqual(self.suffixes, [{
            'suffix': ['.css'],
            'result_mimetype': 'text/css',
            'mimetype': 'text/css',
        }, {
            'suffix': ['.txt'],
            'result_mimetype': 'text/plain',
            'mimetype': 'text/plain',
        }, {
            'suffix': ['.css', '.styl'],
            'result_mimetype': 'text/css',
            'mimetype': None,
        }])

    def test_register_extension_to_none(self):
        self.suffixes.register('.styl', to='text/css')
        self.suffixes.register('.tmpl')
        self.assertItemsEqual(self.suffixes, [{
            'suffix': ['.css'],
            'result_mimetype': 'text/css',
            'mimetype': 'text/css',
        }, {
            'suffix': ['.txt'],
            'result_mimetype': 'text/plain',
            'mimetype': 'text/plain',
        }, {
            'suffix': ['.css', '.styl'],
            'result_mimetype': 'text/css',
            'mimetype': None,
        }, {
            'suffix': ['.css', '.tmpl'],
            'result_mimetype': 'text/css',
            'mimetype': None,
        }, {
            'suffix': ['.txt', '.tmpl'],
            'result_mimetype': 'text/plain',
            'mimetype': None,
        }, {
            'suffix': ['.css', '.styl', '.tmpl'],
            'result_mimetype': 'text/css',
            'mimetype': None,
        }])

    def test_unregister_extension(self):
        self.suffixes.register('.styl', to='text/css')
        self.suffixes.register('.tmpl')
        self.suffixes.unregister('.css')
        self.assertItemsEqual(self.suffixes, [{
            'suffix': ['.txt'],
            'result_mimetype': 'text/plain',
            'mimetype': 'text/plain',
        }, {
            'suffix': ['.txt', '.tmpl'],
            'result_mimetype': 'text/plain',
            'mimetype': None,
        }])

    def test_find_all(self):
        self.suffixes.register('.styl', to='text/css')
        self.assertItemsEqual(self.suffixes.find(), ['.css', '.txt', '.css.styl'])

    def test_find_by_mimetype(self):
        self.suffixes.register('.styl', to='text/css')
        self.assertItemsEqual(self.suffixes.find('text/css'), ['.css', '.css.styl'])
        self.assertItemsEqual(self.suffixes.find('text/plain'), ['.txt'])

    def test_find_nothing(self):
        self.assertItemsEqual(self.suffixes.find('application/javascript'), [])
