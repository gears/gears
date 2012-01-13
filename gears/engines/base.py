import subprocess


class EngineProcessFailed(Exception):
    pass


class BaseEngine(object):

    result_mimetype = None

    def process(self, source, context):
        raise NotImplementedError()


class ExecEngine(BaseEngine):

    executable = None
    params = []

    def __init__(self, executable=None):
        if executable is not None:
            self.executable = executable

    def process(self, source, context):
        p = subprocess.Popen(
            args=self.get_args(context),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        output, errors = p.communicate(input=source)
        if p.returncode == 0:
            return output
        raise EngineProcessFailed(errors)

    def get_args(self, context):
        return [self.executable] + self.params
