class CallStackPopException(Exception):
    pass


class CallStack(object):

    def __init__(self):
        self.sets = [set()]

    def __contains__(self, path):
        return any((path in s) for s in self.sets)

    def add(self, path):
        self.sets[-1].add(path)

    def push(self):
        s = set()
        self.sets.append(s)
        return s

    def pop(self):
        if len(self.sets) == 1:
            raise CallStackPopException
        return self.sets.pop()
