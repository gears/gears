from unittest2 import TestCase

from gears.compat import str
from gears.processors.hexdigest_paths import rewrite_paths

from .helpers import GearsTestCase


class RewritePathsTests(TestCase):

    def check(self, source, expected_result):
        result = rewrite_paths(source, lambda path: 'new/path')
        self.assertEqual(result, expected_result)

    def test_single_quotes(self):
        self.check("url('../images/logo.png')", "url('new/path')")

    def test_double_quotes(self):
        self.check('url("../images/logo.png")', 'url("new/path")')

    def test_without_quotes(self):
        self.check('url(../images/logo.png)', 'url(new/path)')


class HexdigestPathsProcessorTests(GearsTestCase):

    fixtures_root = 'hexdigest_paths_processor'

    def test_process(self):
        asset = self.get_asset('process')
        output = self.get_output('process')
        self.assertEqual(str(asset), output)
