import os
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
            matched_path = self.find_location(root, path)
            if not matched_path or not os.path.isdir(matched_path):
                continue
            for filename in os.listdir(matched_path):
                filepath = os.path.join(matched_path, filename)
                if os.path.isfile(filepath):
                    yield os.path.join(path, filename), filepath
