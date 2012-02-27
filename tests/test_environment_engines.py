from gears.compilers import (
    CoffeeScriptCompiler, HandlebarsCompiler, LessCompiler, StylusCompiler)
from gears.environment import Compilers

from mock import Mock
from unittest2 import TestCase


class CompilersTests(TestCase):

    def setUp(self):
        self.compilers = Compilers()
        self.first_compiler = Mock()
        self.second_compiler = Mock()

    def test_register_defaults(self):
        self.compilers.register_defaults()
        self.assertItemsEqual(self.compilers, ['.coffee', '.handlebars', '.less', '.styl'])
        self.assertIs(self.compilers['.coffee'].handler_class, CoffeeScriptCompiler)
        self.assertIs(self.compilers['.handlebars'].handler_class, HandlebarsCompiler)
        self.assertIs(self.compilers['.less'].handler_class, LessCompiler)
        self.assertIs(self.compilers['.styl'].handler_class, StylusCompiler)

    def test_register(self):
        self.compilers.register('.css', self.first_compiler)
        self.assertIn('.css', self.compilers)
        self.assertIs(self.compilers['.css'], self.first_compiler)

    def test_register_twice(self):
        self.compilers.register('.css', self.first_compiler)
        self.compilers.register('.css', self.second_compiler)
        self.assertIs(self.compilers['.css'], self.second_compiler)

    def test_unregister(self):
        self.compilers.register('.css', self.first_compiler)
        self.compilers.unregister('.css')
        self.assertNotIn('.css', self.compilers)

    def test_unregister_if_does_not_exist(self):
        self.compilers.unregister('.css')
