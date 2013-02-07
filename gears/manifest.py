import os
import errno
import json


class Manifest(object):

    def __init__(self, path):
        self.path = path
        self.data = {}
        self.load()

    @property
    def files(self):
        return self.data.setdefault('files', {})

    def load(self):
        try:
            with open(self.path) as f:
                self.data = json.load(f)
        except IOError as e:
            if e.errno != errno.ENOENT:
                raise

    def dump(self):
        dirpath = os.path.dirname(self.path)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        with open(self.path, 'w') as f:
            json.dump(self.data, f, indent=2)
