from __future__ import with_statement
from gears.utils import safe_join, first, first_or_none
from unittest2 import TestCase


class SafeJoinTests(TestCase):

    def test_if_base_is_not_absolute(self):
        with self.assertRaisesRegexp(ValueError, 'is not an absolute path'):
            safe_join('assets', 'js/script.js')

    def test_if_path_is_outside_of_base(self):
        with self.assertRaisesRegexp(ValueError, 'is outside of'):
            safe_join('/assets', '../js/script.js')

    def test_success(self):
        path = safe_join('/assets', 'js/script.js')
        self.assertEqual(path, '/assets/js/script.js')


class FirstTests(TestCase):

    def test_no_function(self):
        self.assertEqual(first(None, (0, 0, '', 3, None)), 3)

    def test_function(self):
        self.assertEqual(first(lambda x: x == '', (0, 0, '', 3, None)), '')

    def test_no_result(self):
        with self.assertRaisesRegexp(ValueError, 'No suitable value found.'):
            first(lambda x: x == 2, (0, 0, '', 3, None))


class FirstOrNoneTests(TestCase):

    def test_success(self):
        self.assertEqual(first_or_none(lambda x: x == '', (0, 0, '', 3)), '')

    def test_no_result(self):
        self.assertIsNone(first_or_none(lambda x: x == 2, (0, 0, '', 3)))
