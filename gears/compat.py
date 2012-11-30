import sys


is_py2 = (sys.version_info[0] == 2)
is_py3 = (sys.version_info[0] == 3)


class UnicodeMixin(object):
    """Python 3 compatible __str__/__unicode__ support"""

    def __str__(self):
        value = self.__unicode__()
        if is_py2:
            return value.encode('utf-8')
        return value


if is_py2:
    bytes = str
    str = unicode
elif is_py3:
    bytes = bytes
    str = str
