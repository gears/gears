import tempfile
import shutil
from gears.cache import FileBasedCache
from unittest2 import TestCase


class FileBasedCacheTests(TestCase):

    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.cache = FileBasedCache(self.root)

    def tearDown(self):
        shutil.rmtree(self.root)

    def test_saves_value_for_key(self):
        self.cache.set('a', 1)
        self.assertEqual(self.cache.get('a'), 1)

    def test_returns_none_if_key_not_found(self):
        self.assertIsNone(self.cache.get('a'))
