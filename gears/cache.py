from __future__ import with_statement

import hashlib
import os
try:
    import cPickle as pickle
except ImportError:
    import pickle


class SimpleCache(dict):

    def set(self, key, value):
        self[key] = value

    def get(self, key):
        return super(SimpleCache, self).get(key)


class FileBasedCache(object):

    def __init__(self, root):
        self.root = root

    def set(self, key, value):
        filepath = self._get_filepath(key)

        dirname = os.path.dirname(filepath)
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except OSError:
                return

        try:
            with open(filepath, 'wb') as f:
                pickle.dump(value, f, pickle.HIGHEST_PROTOCOL)
        except IOError:
            pass

    def get(self, key):
        filepath = self._get_filepath(key)
        try:
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        except (IOError, OSError, EOFError, pickle.PickleError):
            return None

    def _get_filepath(self, key):
        relpath = hashlib.sha1(key).hexdigest()
        relpath = os.path.join(relpath[:2], relpath[2:4], relpath[4:])
        return os.path.join(self.root, relpath)
