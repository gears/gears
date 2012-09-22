from __future__ import with_statement

import os

from gears.assets import Requirements, Asset
from gears.compilers import BaseCompiler
from gears.environment import Environment
from gears.finders import FileSystemFinder
from gears.processors import DirectivesProcessor

from unittest2 import TestCase


TESTS_DIR = os.path.dirname(__file__)
FIXTURES_DIR = os.path.join(TESTS_DIR, 'fixtures', 'directives_processor')


class FakeLessCompiler(BaseCompiler):

    result_mimetype = 'text/css'

    def __call__(self, asset):
        pass


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

    def get_asset(self, fixture, source='source.js'):
        if isinstance(fixture, Environment):
            environment = fixture
        else:
            environment = self.get_environment(fixture)
        return Asset(*environment.find(source))

    def get_source(self, fixture, filename):
        fixture_path = self.get_fixture_path(fixture)
        with open(os.path.join(fixture_path, filename)) as f:
            return f.read()

    def test_fills_asset_requirements(self):
        asset = self.get_asset('requirements')
        DirectivesProcessor.as_handler()(asset)
        self.check_paths(asset.requirements.before, ['js/external.js'])
        self.check_paths(asset.requirements.after, [
            'js/libs/simple_lib.js',
            'js/libs/useful_lib.js',
            'js/models.js',
            'js/views.js',
            'js/utils/a.js',
            'js/utils/b/a.js',
            'js/utils/b/b.js',
        ])

    def test_modifies_processed_source(self):
        asset = self.get_asset('requirements')
        DirectivesProcessor.as_handler()(asset)
        self.assertEqual(
            asset.processed_source,
            self.get_source('requirements', 'output.js'),
        )

    def test_modifies_bundled_source(self):
        asset = self.get_asset('requirements')
        DirectivesProcessor.as_handler()(asset)
        self.assertEqual(
            asset.bundled_source,
            self.get_source('requirements', 'bundle.js'),
        )

    def test_requires_asset_only_once(self):
        asset = self.get_asset('require_multiple_times')
        DirectivesProcessor.as_handler()(asset)
        self.check_paths(
            list(asset.requirements),
            'external.js models.js views.js source.js'.split(),
        )

    def test_depend_on_directive(self):
        environment = self.get_environment('depend_on')
        environment.compilers.register('.less', FakeLessCompiler.as_handler())
        asset = self.get_asset(environment, 'source.less')
        DirectivesProcessor.as_handler()(asset)
        self.assertItemsEqual(asset.dependencies.to_list(), [
            os.path.join(os.path.dirname(asset.absolute_path), 'mixins/colors.less'),
        ])
