import errno
from StringIO import StringIO
from gears.manifest import Manifest
from mock import MagicMock, patch
from unittest2 import TestCase


class ManifestTests(TestCase):

    def setUp(self):
        self.open = MagicMock()
        self.open_patch = patch('__builtin__.open', self.open)
        self.open_patch.start()

    def tearDown(self):
        self.open_patch.stop()

    def test_loads_data(self):
        self.open.return_value.__enter__.return_value = StringIO("""{
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

    def test_fails_silently_if_file_not_found(self):
        self.open.side_effect = IOError(errno.ENOENT, 'No such file or directory')
        manifest = Manifest('manifest.json')
