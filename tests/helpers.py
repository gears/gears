import codecs
import os
import unittest2

from gears.asset_attributes import AssetAttributes
from gears.assets import Asset, StaticAsset
from gears.environment import Environment
from gears.finders import FileSystemFinder


TESTS_DIR = os.path.dirname(__file__)
FIXTURES_DIR = os.path.join(TESTS_DIR, 'fixtures')


def read(path, encoding='utf-8', mode='r'):
    with codecs.open(path, encoding=encoding, mode=mode) as file:
        return file.read()


class GearsTestCase(unittest2.TestCase):

    fixtures_root = None

    def get_fixture_path(self, fixture):
        return os.path.join(FIXTURES_DIR, self.fixtures_root, fixture)

    def find_fixture_file(self, fixture, name):
        fixture_path = self.get_fixture_path(fixture)
        for dirpath, dirnames, filenames in os.walk(fixture_path):
            for filename in filenames:
                if filename.split('.')[0] == name:
                    return os.path.join(dirpath, filename)
        return None

    def get_source_path(self, fixture):
        return self.find_fixture_file(fixture, 'source')

    def get_source(self, fixture):
        return read(self.get_source_path(fixture))

    def get_output(self, fixture, name='output'):
        return read(self.find_fixture_file(fixture, name))

    def get_finder(self, fixture):
        fixture_path = self.get_fixture_path(fixture)
        return FileSystemFinder([fixture_path])

    def get_environment(self, fixture):
        finder = self.get_finder(fixture)
        environment = Environment(os.path.join(TESTS_DIR, 'static'))
        environment.finders.register(finder)
        environment.register_defaults()
        return environment

    def get_asset(self, fixture, environment=None, asset_class=Asset):
        source_path = self.get_source_path(fixture)
        if environment is None:
            environment = self.get_environment(fixture)

        fixture_path = self.get_fixture_path(fixture)
        logical_path = os.path.relpath(source_path, fixture_path)
        asset_attributes = AssetAttributes(environment, logical_path)

        return asset_class(asset_attributes, source_path)

    def get_static_asset(self, fixture, environment=None):
        return self.get_asset(fixture, environment, asset_class=StaticAsset)
