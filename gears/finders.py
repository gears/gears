import os
from .exceptions import ImproperlyConfigured
from .utils import safe_join


class BaseFinder(object):

    def find(self, path, all=False):
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

    def find(self, path, all=False):
        matches = []
        for root in self.locations:
            matched_path = self.find_location(root, path)
            if matched_path:
                if not all:
                    return matched_path
                matches.append(matched_path)
        return matches

    def find_location(self, root, path):
        path = safe_join(root, path)
        if os.path.exists(path):
            return path
