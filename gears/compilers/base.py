import subprocess
from ..asset_handler import BaseAssetHandler


class CompilerFailed(Exception):
    pass


class BaseCompiler(BaseAssetHandler):

    result_mimetype = None

    @classmethod
    def as_handler(cls, **initkwargs):
        handler = super(BaseCompiler, cls).as_handler(**initkwargs)
        handler.result_mimetype = cls.result_mimetype
        return handler


class ExecCompiler(BaseCompiler):

    executable = None
    params = []

    def __init__(self, executable=None):
        if executable is not None:
            self.executable = executable

    def __call__(self, asset):
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
