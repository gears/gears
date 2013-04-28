import os
from gears.assets import Dependencies
from .helpers import GearsTestCase


class AssetDependenciesTests(GearsTestCase):

    fixtures_root = 'asset_dependencies'

    def test_adds_dependency_only_once(self):
        fixture_file = self.find_fixture_file('adds_dependency_only_once', 'dependency')
        dependencies = Dependencies(self.get_environment('adds_dependency_only_once'))
        dependencies.add(fixture_file)
        dependencies.add(fixture_file)
        self.assertEqual(len(dependencies._registry), 1)
