from __future__ import with_statement
import hashlib
import os


def path_content(path):
    if os.path.isdir(path):
        return ', '.join(os.listdir(path))
    with open(path) as f:
        return f.read()


def path_hexdigest(path):
    return hashlib.sha1(path_content(path)).hexdigest()


def path_mtime(path):
    try:
        return os.stat(path).st_mtime
    except OSError:
        pass


class Cache(dict):

    def __call__(self, absolute_path, source, dependencies=None):
        try:
            self[absolute_path] = {
                'dependencies': tuple(dependencies or ()),
                'hexdigest': path_hexdigest(absolute_path),
                'mtime': path_mtime(absolute_path),
                'source': source}
        except IOError:
            pass

    def is_cached(self, absolute_path):
        return absolute_path in self

    def is_mtime_changed(self, absolute_path):
        mtime = path_mtime(absolute_path)
        return not mtime or mtime > self[absolute_path]['mtime']

    def is_hexdigest_changed(self, absolute_path):
        hexdigest = path_hexdigest(absolute_path)
        return hexdigest != self[absolute_path]['hexdigest']

    def is_content_changed(self, absolute_path):
        return (self.is_mtime_changed(absolute_path) and
                self.is_hexdigest_changed(absolute_path))

    def are_dependencies_modified(self, absolute_path):
        dependencies = self[absolute_path]['dependencies']
        return any(self.is_modified(path) for path in dependencies)

    def is_modified(self, absolute_path):
        return (not self.is_cached(absolute_path) or
                self.is_content_changed(absolute_path) or
                self.are_dependencies_modified(absolute_path))

    def get_source(self, absolute_path):
        return self[absolute_path]['source']
