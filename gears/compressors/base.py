import subprocess
from functools import wraps


class CompressorFailed(Exception):
    pass


class BaseCompressor(object):

    result_mimetype = None

    @classmethod
    def as_compressor(cls, **initkwargs):
        @wraps(cls, updated=())
        def compressor(source):
            return compressor.compressor_class(**initkwargs).compress(source)
        compressor.compressor_class = cls
        return compressor

    def compress(self, source):
        raise NotImplementedError()


class ExecCompressor(BaseCompressor):

    executable = None
    params = []

    def __init__(self, executable=None):
        if executable is not None:
            self.executable = executable

    def compress(self, source):
        self.source = source
        p = subprocess.Popen(
            args=self.get_args(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        output, errors = p.communicate(input=source.encode('utf-8'))
        if p.returncode != 0:
            raise CompressorFailed(errors)
        return output.decode('utf-8')

    def get_args(self):
        return [self.executable] + self.params
