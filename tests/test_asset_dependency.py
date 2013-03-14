import os
from gears.assets import Dependency
from .helpers import GearsTestCase


class AssetDependencyTests(GearsTestCase):

    fixtures_root = 'asset_dependency'

    def test_dependencies_with_the_same_path_are_equal(self):
        fixture = 'dependencies_with_the_same_path_are_equal'
        environment = self.get_environment(fixture)
        fixture_file = self.find_fixture_file(fixture, 'dependency')
        dependency1 = Dependency(environment, fixture_file)
        dependency2 = Dependency(environment, fixture_file)
        self.assertEqual(dependency1, dependency1)

    def test_handles_directories(self):
        fixture = 'handles_directories'
        fixture_path = self.get_fixture_path(fixture)
        environment = self.get_environment(fixture)
        Dependency(environment, os.path.join(fixture_path, 'libs'))

    def test_handles_binary_files(self):
        fixture = 'handles_binary_files'
        fixture_path = self.get_fixture_path(fixture)
        environment = self.get_environment(fixture)
        Dependency(environment, os.path.join(fixture_path, 'image.png'))
