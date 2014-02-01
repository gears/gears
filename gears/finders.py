import os
import glob2
from .exceptions import ImproperlyConfigured, FileNotFound
from .utils import safe_join


class BaseFinder(object):

    def find(self, path):
        raise NotImplementedError()


class FileSystemFinder(BaseFinder):

    def __init__(self, directories):
        self.locations = []
        if not isinstance(directories, (list, tuple)):
            raise ImproperlyConfigured(
                "FileSystemFinder's 'directories' parameter is not a "
                "tuple or list; perhaps you forgot a trailing comma?")
        for directory in directories:
            if directory not in self.locations:
                self.locations.append(directory)

    @property
    def paths(self):
        return self.locations

    def find(self, path):
        for matched_path in self.find_all(path):
            return matched_path
        raise FileNotFound(path)

    def find_all(self, path):
        for root in self.locations:
            matched_path = self.find_location(root, path)
            if matched_path:
                yield matched_path

    def find_location(self, root, path):
        path = safe_join(root, path)
        if os.path.exists(path):
            return path

    def list(self, path):
        for root in self.locations:
            for absolute_path in glob2.iglob(safe_join(root, path)):
                if os.path.isfile(absolute_path):
                    logical_path = os.path.relpath(absolute_path, root)
                    yield logical_path, absolute_path
