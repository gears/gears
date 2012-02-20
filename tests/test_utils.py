from __future__ import with_statement
from gears.utils import safe_join
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
