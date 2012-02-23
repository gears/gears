import os


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
