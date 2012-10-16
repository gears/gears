from gears.asset_handler import AssetHandlerError, ExecMixin
from mock import patch, Mock
from unittest2 import TestCase


class Exec(ExecMixin):
    executable = 'program'


class ExecMixinTests(TestCase):

    @patch('gears.asset_handler.Popen')
    def test_returns_stdout_on_success(self, Popen):
        result = Mock()
        result.returncode = 0
        result.communicate.return_value = (b'output', b'')
        Popen.return_value = result
        self.assertEqual(Exec().run('input'), 'output')

    @patch('gears.asset_handler.Popen')
    def test_raises_stderr_on_failure(self, Popen):
        result = Mock()
        result.returncode = 1
        result.communicate.return_value = (b'', b'error')
        Popen.return_value = result
        with self.assertRaises(AssetHandlerError):
            Exec().run('input')
