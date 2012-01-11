from __future__ import with_statement

import os

from gears.exceptions import ImproperlyConfigured, FileNotFound
from gears.finders import FileSystemFinder

from mock import patch, Mock
from unittest2 import TestCase


ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'assets'))


class FileSystemFinderTests(TestCase):

    def test_initialization(self):
        finder = FileSystemFinder(('/first', '/second', '/third', '/first'))
        self.assertEqual(finder.locations, ['/first', '/second', '/third'])

    def test_if_directories_is_not_iterable(self):
        with self.assertRaises(ImproperlyConfigured):
            finder = FileSystemFinder('/first')

    @patch('os.path.exists')
    def test_find_location_if_exists(self, exists):
        exists.return_value = True
        finder = FileSystemFinder(('/assets',))
        location = finder.find_location('/assets', 'js/script.js')
        self.assertEqual(location, '/assets/js/script.js')
        exists.assert_called_once_with('/assets/js/script.js')

    @patch('os.path.exists')
    def test_find_location_if_does_not_exist(self, exists):
        exists.return_value = False
        finder = FileSystemFinder(('/assets',))
        self.assertIsNone(finder.find_location('/assets', 'js/script.js'))
        exists.assert_called_once_with('/assets/js/script.js')

    def test_find_if_exists(self):
        finder = FileSystemFinder(('/first', '/second', '/third'))
        finder.find_all = Mock(return_value=(
            '/second/js/script.js', '/third/js/script.js'))
        self.assertEqual(finder.find('js/script.js'), '/second/js/script.js')
        finder.find_all.assert_called_once_with('js/script.js')

    def test_find_if_does_not_exist(self):
        finder = FileSystemFinder(('/first', '/second', '/third'))
        finder.find_all = Mock(return_value=())
        with self.assertRaises(FileNotFound):
            finder.find('js/script.js')
        finder.find_all.assert_called_once_with('js/script.js')

    def test_find_all_if_exists(self):

        def find_location(root, path):
            if root != '/first':
                return os.path.join(root, path)

        finder = FileSystemFinder(('/first', '/second', '/third'))
        finder.find_location = Mock(side_effect=find_location)

        paths = list(finder.find_all('js/script.js'))
        self.assertEqual(paths, ['/second/js/script.js', '/third/js/script.js'])
        self.assertEqual(finder.find_location.call_args_list, [
            (('/first', 'js/script.js'), {}),
            (('/second', 'js/script.js'), {}),
            (('/third', 'js/script.js'), {})])

    def test_find_all_if_does_not_exist(self):
        finder = FileSystemFinder(('/first', '/second', '/third'))
        finder.find_location = Mock(return_value=False)

        self.assertEqual(list(finder.find_all('js/script.js')), [])
        self.assertEqual(finder.find_location.call_args_list, [
            (('/first', 'js/script.js'), {}),
            (('/second', 'js/script.js'), {}),
            (('/third', 'js/script.js'), {})])

    def test_find(self):
        finder = FileSystemFinder([ASSETS_DIR])
        self.assertItemsEqual(finder.list('js/templates'), (
            ('js/templates/readme.txt', os.path.join(ASSETS_DIR, 'js/templates/readme.txt')),
            ('js/templates/a.js.handlebars', os.path.join(ASSETS_DIR, 'js/templates/a.js.handlebars')),
            ('js/templates/b.js.handlebars', os.path.join(ASSETS_DIR, 'js/templates/b.js.handlebars')),
            ('js/templates/c.js.handlebars', os.path.join(ASSETS_DIR, 'js/templates/c.js.handlebars')),
        ))
