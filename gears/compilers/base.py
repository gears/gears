import subprocess
from functools import wraps


class CompilerFailed(Exception):
    pass


class BaseCompiler(object):

    result_mimetype = None

    @classmethod
    def as_compiler(cls, **initkwargs):
        @wraps(cls, updated=())
        def compiler(asset):
            instance = compiler.compiler_class(**initkwargs)
            return instance.process(asset)
        compiler.compiler_class = cls
        compiler.result_mimetype = cls.result_mimetype
        return compiler

    def process(self, asset):
        raise NotImplementedError()


class ExecCompiler(BaseCompiler):

    executable = None
    params = []

    def __init__(self, executable=None):
        if executable is not None:
            self.executable = executable

    def process(self, asset):
        self.asset = asset
        p = subprocess.Popen(
            args=self.get_args(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        output, errors = p.communicate(input=asset.processed_source.encode('utf-8'))
        if p.returncode != 0:
            raise CompilerFailed(errors)
        asset.processed_source = output.decode('utf-8')

    def get_args(self):
        return [self.executable] + self.params
