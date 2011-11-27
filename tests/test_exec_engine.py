from __future__ import with_statement
from gears.engines.base import ExecEngine, EngineProcessFailed
from mock import Mock, patch
from unittest2 import TestCase


class ExecEnginesTests(TestCase):

    def test_executable(self):

        class Engine(ExecEngine):
            executable = 'default'

        self.assertEqual(Engine().executable, 'default')
        self.assertEqual(Engine('custom').executable, 'custom')

    @patch('subprocess.PIPE')
    @patch('subprocess.Popen')
    def test_process_success(self, Popen, PIPE):
        p = Mock()
        p.returncode = 0
        p.communicate.return_value = ('output', 'errors')
        Popen.return_value = p

        class Engine(ExecEngine):
            executable = 'command'
            params = ['--compile']

        self.assertEqual(Engine().process('source', {}, set()), 'output')
        Popen.assert_called_once_with(args=['command', '--compile'],
                                      stdin=PIPE, stdout=PIPE, stderr=PIPE)
        p.communicate.assert_called_once_with(input='source')

    @patch('subprocess.PIPE')
    @patch('subprocess.Popen')
    def test_process_fail(self, Popen, PIPE):
        p = Mock()
        p.returncode = 1
        p.communicate.return_value = ('output', 'errors')
        Popen.return_value = p

        class Engine(ExecEngine):
            executable = 'command'
            params = ['--compile']

        with self.assertRaisesRegexp(EngineProcessFailed, r'^errors$'):
            Engine().process('source', {}, set())
