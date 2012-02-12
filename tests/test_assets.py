from __future__ import with_statement

import codecs
import os

from gears.assets import CircularDependencyError, Asset
from gears.environment import Environment
from gears.finders import FileSystemFinder
from gears.processors import DirectivesProcessor

from unittest2 import TestCase


TESTS_DIR = os.path.dirname(__file__)
FIXTURES_DIR = os.path.join(TESTS_DIR, 'fixtures', 'assets')


def read(file):
    with codecs.open(file, encoding='utf-8') as f:
        return f.read()


class AssetTests(TestCase):

    def get_fixture_path(self, fixture):
        return os.path.join(FIXTURES_DIR, fixture)

    def get_finder(self, fixture):
        return FileSystemFinder([self.get_fixture_path(fixture)])

    def get_environment(self, fixture):
        environment = Environment(os.path.join(TESTS_DIR, 'static'))
        environment.finders.register(self.get_finder(fixture))
        environment.mimetypes.register_defaults()
        environment.preprocessors.register_defaults()
        return environment

    def get_asset(self, fixture):
        return Asset(*self.get_environment(fixture).find('source.js'))

    def test_circular_dependency(self):
        with self.assertRaises(CircularDependencyError):
            asset = self.get_asset('circular_dependency')

    def test_unicode_support(self):
        output = read(os.path.join(FIXTURES_DIR, 'unicode_support', 'output.js'))
        self.assertEqual(unicode(self.get_asset('unicode_support')), output)
