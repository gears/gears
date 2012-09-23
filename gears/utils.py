import os
import re


missing = object()


class cached_property(object):

    def __init__(self, func):
        self.func = func
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__
        self.__module__ = func.__module__

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__, missing)
        if value is missing:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value


def safe_join(base, *paths):
    if not os.path.isabs(base):
        raise ValueError("%r is not an absolute path." % base)
    base = os.path.normpath(base)
    path = os.path.normpath(os.path.join(base, *paths))
    if not path.startswith(base):
        raise ValueError("Path %r is outside of %r" % (path, base))
    return path


def unique(iterable, key=lambda x: x):
    yielded = set()
    for item in iterable:
        keyitem = key(item)
        if keyitem not in yielded:
            yielded.add(keyitem)
            yield item


def listdir(path, recursive=False):
    for dirpath, dirnames, filenames in os.walk(path):
        if not recursive:
            dirnames[:] = []
        dirpath = os.path.relpath(dirpath, path)
        for filename in filenames:
            yield os.path.normpath(os.path.join(dirpath, filename))


def get_condition_func(condition):
    if callable(condition):
        return condition
    if isinstance(condition, basestring):
        condition = re.compile(condition)
    return lambda path: condition.search(path)
