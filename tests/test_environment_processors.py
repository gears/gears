from gears.environment import Processors, Preprocessors
from gears.processors import DirectivesProcessor

from mock import Mock
from unittest2 import TestCase


class ProcessorsTests(TestCase):

    def setUp(self):
        self.processors = Processors()
        self.first_processor = Mock()
        self.second_processor = Mock()
        self.third_processor = Mock()

    def test_register(self):
        self.processors.register('text/css', self.first_processor)
        self.processors.register('text/css', self.second_processor)
        self.processors.register('text/plain', self.third_processor)
        self.assertIn('text/css', self.processors)
        self.assertEqual(self.processors['text/css'], [self.first_processor, self.second_processor])
        self.assertIn('text/plain', self.processors)
        self.assertEqual(self.processors['text/plain'], [self.third_processor])

    def test_register_twice(self):
        self.processors.register('text/css', self.first_processor)
        self.processors.register('text/css', self.first_processor)
        self.assertEqual(self.processors['text/css'], [self.first_processor])

    def test_unregister(self):
        self.processors.register('text/css', self.first_processor)
        self.processors.register('text/css', self.second_processor)
        self.processors.unregister('text/css', self.first_processor)
        self.assertEqual(self.processors['text/css'], [self.second_processor])

    def test_unregister_if_does_not_exist(self):
        self.processors.unregister('text/css', self.first_processor)

    def test_get_if_exists(self):
        self.processors.register('text/css', self.first_processor)
        self.processors.register('text/css', self.second_processor)
        self.assertEqual(self.processors.get('text/css'), [self.first_processor, self.second_processor])

    def test_get_if_does_not_exist(self):
        self.assertEqual(self.processors.get('text/css'), [])


class PreprocessorsTests(TestCase):

    def setUp(self):
        self.preprocessors = Preprocessors()

    def test_register_defaults(self):
        self.preprocessors.register_defaults()
        self.assertItemsEqual(self.preprocessors.keys(), ['text/css', 'application/javascript'])
        self.assertEqual(
            [p.handler_class for p in self.preprocessors['text/css']],
            [DirectivesProcessor])
        self.assertEqual(
            [p.handler_class for p in self.preprocessors['application/javascript']],
            [DirectivesProcessor])
