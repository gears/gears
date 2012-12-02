import os

from gears.compilers import BaseCompiler
from gears.processors import DirectivesProcessor

from .helpers import GearsTestCase


class FakeLessCompiler(BaseCompiler):

    result_mimetype = 'text/css'

    def __call__(self, asset):
        pass


class DirectivesProcessorTests(GearsTestCase):

    fixtures_root = 'directives_processor'

    def check_paths(self, assets, paths):
        self.assertEqual([asset.attributes.path for asset in assets], paths)

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
            self.get_output('requirements'),
        )

    def test_modifies_bundled_source(self):
        asset = self.get_asset('requirements')
        DirectivesProcessor.as_handler()(asset)
        self.assertEqual(
            asset.bundled_source,
            self.get_output('requirements', 'bundle'),
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
        asset = self.get_asset('depend_on', environment)
        DirectivesProcessor.as_handler()(asset)
        self.assertItemsEqual(asset.dependencies.to_list(), [
            os.path.join(os.path.dirname(asset.absolute_path), 'mixins/colors.less'),
        ])
