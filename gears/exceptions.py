class ImproperlyConfigured(Exception):
    pass


class FileNotFound(Exception):
    pass


class GearsUnicodeError(Exception):

    def __init__(self, path, msg):
        self.path = path
        self.msg = msg

    def __str__(self):
        return '%s: %s' % (self.path, self.msg)
