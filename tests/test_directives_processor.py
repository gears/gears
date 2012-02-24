from __future__ import with_statement

import os

from gears.assets import Requirements, Asset
from gears.environment import Environment
from gears.finders import FileSystemFinder
from gears.processors import DirectivesProcessor

from unittest2 import TestCase


TESTS_DIR = os.path.dirname(__file__)
FIXTURES_DIR = os.path.join(TESTS_DIR, 'fixtures', 'directives_processor')


class DirectivesProcessorTests(TestCase):

    def check_paths(self, assets, paths):
        self.assertEqual([asset.attributes.path for asset in assets], paths)

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

    def get_output_source(self, fixture):
        fixture_path = self.get_fixture_path(fixture)
        with open(os.path.join(fixture_path, 'output.js')) as f:
            return f.read()

    def test_fills_asset_requirements(self):
        asset = self.get_asset('requirements')
        DirectivesProcessor.as_handler()(asset)
        self.check_paths(asset.requirements.before, ['js/external.js'])
        self.check_paths(asset.requirements.after, ['js/models.js', 'js/views.js'])

    def test_modifies_processed_source(self):
        asset = self.get_asset('requirements')
        DirectivesProcessor.as_handler()(asset)
        self.assertEqual(asset.processed_source, self.get_output_source('requirements'))

    def test_requires_asset_only_once(self):
        asset = self.get_asset('require_multiple_times')
        DirectivesProcessor.as_handler()(asset)
        self.check_paths(list(asset.requirements), 'external.js models.js views.js source.js'.split())
