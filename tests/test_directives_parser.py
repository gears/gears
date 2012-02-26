from __future__ import with_statement

import os
from gears.directives_parser import DirectivesParser
from unittest2 import TestCase


TESTS_DIR = os.path.dirname(__file__)
FIXTURES_DIR = os.path.join(TESTS_DIR, 'fixtures', 'directives_parser')


def read(file):
    with open(file) as f:
        return f.read()


class DirectivesParserTests(TestCase):

    def get_fixture_files(self, path):
        files = {}
        for filename in os.listdir(path):
            files[filename.split('.')[0]] = os.path.join(path, filename)
        return files['source'], files['output']

    def get_fixture(self, fixture):
        fixture_path = os.path.join(FIXTURES_DIR, fixture)
        return map(read, self.get_fixture_files(fixture_path))

    def check_asset(self, fixture, directives):
        source, output = self.get_fixture(fixture)
        result = DirectivesParser().parse(source)
        self.assertEqual(result[0], directives)
        self.assertEqual(result[1], output)

    def test_does_nothing_if_no_directives(self):
        self.check_asset('no_directives', [])

    def test_strips_whitespaces(self):
        self.check_asset('whitespaces', [])

    def test_multiline_comments(self):
        self.check_asset('multiline_comments', [
            'require reset',
            'require base',
        ])

    def test_handles_slash_comments(self):
        self.check_asset('slash_comments', [
            'require jquery',
            'require underscore'
        ])

    def test_handles_dash_comments(self):
        self.check_asset('dash_comments', [
            'require jquery',
            'require_tree .',
        ])

    def test_handle_multiple_comments(self):
        self.check_asset('multiple_comments', [
            'require jquery',
            'require underscore',
            'require backbone',
            'require models',
            'require collections',
            'require views',
        ])

    def test_skips_non_header_comments(self):
        self.check_asset('non_header_comments', ['require jquery'])


class DirectivesParserHeaderPatternTests(TestCase):

    def setUp(self):
        self.re = DirectivesParser().header_re

    def test_matches_multiline_comment(self):
        self.assertTrue(self.re.match('\n\n/*\nmultiline comment\n */'))

    def test_matches_multiple_miltiline_comments(self):
        self.assertTrue(self.re.match('/* comment */\n\n/* comment */'))

    def test_matches_slash_comment(self):
        self.assertTrue(self.re.match('  // this\n\n  // is\n  // comment'))

    def test_matches_dash_comment(self):
        self.assertTrue(self.re.match('  # this\n  \n  # is\n  # comment'))


class DirectivesParserDirectivePatternTests(TestCase):

    def setUp(self):
        self.re = DirectivesParser().directive_re

    def test_matches_directives(self):
        self.assertTrue(self.re.match(' *= require jquery'))
        self.assertTrue(self.re.match(' * =require jquery'))
        self.assertTrue(self.re.match('//= require jquery'))
        self.assertTrue(self.re.match(' #= require jquery'))
