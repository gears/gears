import os
from unittest2 import TestCase

from gears.assets import Dependency
from gears.environment import Environment
from gears.finders import FileSystemFinder


TESTS_DIR = os.path.dirname(__file__)
FIXTURES_DIR = os.path.join(TESTS_DIR, 'fixtures', 'asset_dependency')


class AssetDependencyTests(TestCase):

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

    def test_dependencies_with_the_same_path_are_equal(self):
        fixture = 'dependencies_with_the_same_path_are_equal'
        fixture_path = self.get_fixture_path(fixture)
        environment = self.get_environment(fixture)
        path = os.path.join(fixture_path, 'dependency.js')
        self.assertEqual(Dependency(environment, path), Dependency(environment, path))

    def test_handles_directories(self):
        fixture = 'handles_directories'
        fixture_path = self.get_fixture_path(fixture)
        environment = self.get_environment(fixture)
        Dependency(environment, os.path.join(fixture_path, 'libs'))
