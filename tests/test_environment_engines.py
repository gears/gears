from gears.engines import (
    CoffeeScriptEngine, HandlebarsEngine, LessEngine, StylusEngine)
from gears.environment import Engines

from mock import Mock
from unittest2 import TestCase


class EnginesTests(TestCase):

    def setUp(self):
        self.engines = Engines()
        self.first_engine = Mock()
        self.second_engine = Mock()

    def test_register_defaults(self):
        self.engines.register_defaults()
        self.assertItemsEqual(
            self.engines, ['.coffee', '.handlebars', '.less', '.styl'])
        self.assertIs(self.engines['.coffee'], CoffeeScriptEngine)
        self.assertIs(self.engines['.handlebars'], HandlebarsEngine)
        self.assertIs(self.engines['.less'], LessEngine)
        self.assertIs(self.engines['.styl'], StylusEngine)

    def test_register(self):
        self.engines.register('.css', self.first_engine)
        self.assertIn('.css', self.engines)
        self.assertIs(self.engines['.css'], self.first_engine)

    def test_register_twice(self):
        self.engines.register('.css', self.first_engine)
        self.engines.register('.css', self.second_engine)
        self.assertIs(self.engines['.css'], self.second_engine)

    def test_unregister(self):
        self.engines.register('.css', self.first_engine)
        self.engines.unregister('.css')
        self.assertNotIn('.css', self.engines)

    def test_unregister_if_does_not_exist(self):
        self.engines.unregister('.css')
