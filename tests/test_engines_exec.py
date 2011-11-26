from gears.engines.base import ExecEngine
from unittest2 import TestCase


class ExecEnginesTests(TestCase):

    def test_executable(self):

        class Engine(ExecEngine):
            executable = 'default'

        self.assertEqual(Engine().executable, 'default')
        self.assertEqual(Engine('custom').executable, 'custom')
