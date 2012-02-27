import subprocess
from ..asset_handler import BaseAssetHandler


class CompressorFailed(Exception):
    pass


class BaseCompressor(BaseAssetHandler):
    pass


class ExecCompressor(BaseCompressor):

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
        output, errors = p.communicate(input=self.asset.bundled_source.encode('utf-8'))
        if p.returncode != 0:
            raise CompressorFailed(errors)
        return output.decode('utf-8')

    def get_args(self):
        return [self.executable] + self.params
