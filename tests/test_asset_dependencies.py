import os
from unittest2 import TestCase

from gears.assets import Dependencies
from gears.environment import Environment
from gears.finders import FileSystemFinder


TESTS_DIR = os.path.dirname(__file__)
FIXTURES_DIR = os.path.join(TESTS_DIR, 'fixtures', 'asset_dependencies')


class AssetDependenciesTests(TestCase):

    def get_fixture_path(self, fixture):
        return os.path.join(FIXTURES_DIR, fixture)

    def get_finder(self, fixture):
        return FileSystemFinder([self.get_fixture_path(fixture)])

    def get_environment(self, fixture):
        environment = Environment(os.path.join(TESTS_DIR, 'static'))
        environment.finders.register(self.get_finder(fixture))
        environment.mimetypes.register_defaults()
        return environment

    def test_adds_dependency_only_once(self):
        fixture_path = self.get_fixture_path('adds_dependency_only_once')
        dependencies = Dependencies(self.get_environment('adds_dependency_only_once'))
        dependencies.add(os.path.join(fixture_path, 'dependency.js'))
        dependencies.add(os.path.join(fixture_path, 'dependency.js'))
        self.assertEqual(len(dependencies._registry), 1)
