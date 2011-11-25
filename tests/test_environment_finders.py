from gears.environment import Finders
from mock import Mock
from unittest2 import TestCase


class FindersTests(TestCase):

    def setUp(self):
        self.finders = Finders()
        self.first_finder = Mock()
        self.second_finder = Mock()

    def test_register(self):
        self.finders.register(self.first_finder)
        self.finders.register(self.second_finder)
        self.assertEqual(self.finders, [self.first_finder, self.second_finder])

    def test_register_twice(self):
        self.finders.register(self.first_finder)
        self.finders.register(self.first_finder)
        self.assertEqual(self.finders, [self.first_finder])

    def test_unregister(self):
        self.finders.register(self.first_finder)
        self.finders.unregister(self.first_finder)
        self.assertEqual(self.finders, [])
