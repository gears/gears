from unittest2 import TestCase

from gears.compat import str
from gears.processors.semicolons import needs_semicolon

from .helpers import GearsTestCase


class NeedsSemicolonsTests(TestCase):

    def test_blank_source(self):
        self.assertFalse(needs_semicolon(' \t\n'))

    def test_source_with_semicolon(self):
        self.assertFalse(needs_semicolon('x;\n '))

    def test_source_without_semicolon(self):
        self.assertTrue(needs_semicolon('x\n'))


class SemicolonsProcessorTests(GearsTestCase):

    fixtures_root = 'semicolons_processor'

    def test_process(self):
        asset = self.get_asset('process')
        output = self.get_output('process')
        self.assertEqual(str(asset), output)
