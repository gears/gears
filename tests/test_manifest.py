import errno
import mock

from gears.compat import StringIO
from gears.manifest import Manifest

from unittest2 import TestCase


@mock.patch('gears.compat.builtins.open')
class ManifestTests(TestCase):

    def test_loads_data(self, open):
        open.return_value.__enter__.return_value = StringIO("""{
            "files": {
                "css/style.css": "css/style.123456.css",
                "js/script.js": "js/script.654321.js"
            }
        }""")
        manifest = Manifest('manifest.json')
        self.assertEqual(manifest.files, {
            'css/style.css': 'css/style.123456.css',
            'js/script.js': 'js/script.654321.js',
        })

    def test_fails_silently_if_file_not_found(self, open):
        open.side_effect = IOError(errno.ENOENT, 'No such file or directory')
        manifest = Manifest('manifest.json')
