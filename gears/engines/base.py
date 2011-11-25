from subprocess import Popen, PIPE


class EngineProcessFailed(Exception):
    pass


class BaseEngine(object):

    result_mimetype = None

    def process(self, source, context, calls):
        raise NotImplementedError()


class ExecEngine(BaseEngine):

    params = []

    def __init__(self, executable):
        self.executable = executable

    def process(self, source, context, calls):
        args = [self.executable] + self.params
        p = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, errors = p.communicate(input=source)
        if p.returncode == 0:
            return output
        raise EngineProcessFailed(errors)
