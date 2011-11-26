import subprocess


class EngineProcessFailed(Exception):
    pass


class BaseEngine(object):

    result_mimetype = None

    def process(self, source, context, calls):
        raise NotImplementedError()


class ExecEngine(BaseEngine):

    executable = None
    params = []

    def __init__(self, executable=None):
        if executable is not None:
            self.executable = executable

    def process(self, source, context, calls):
        p = subprocess.Popen(
            args=[self.executable] + self.params,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        output, errors = p.communicate(input=source)
        if p.returncode == 0:
            return output
        raise EngineProcessFailed(errors)
