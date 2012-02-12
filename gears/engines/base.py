import subprocess
from functools import wraps


class EngineProcessFailed(Exception):
    pass


class BaseEngine(object):

    result_mimetype = None

    @classmethod
    def as_engine(cls, **initkwargs):
        @wraps(cls, updated=())
        def engine(asset):
            instance = engine.engine_class(**initkwargs)
            return instance.process(asset)
        engine.engine_class = cls
        engine.result_mimetype = cls.result_mimetype
        return engine

    def process(self, asset):
        raise NotImplementedError()


class ExecEngine(BaseEngine):

    executable = None
    params = []

    def __init__(self, executable=None):
        if executable is not None:
            self.executable = executable

    def process(self, asset):
        p = subprocess.Popen(
            args=self.get_args(asset.get_context()),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        output, errors = p.communicate(input=asset.processed_source)
        if p.returncode == 0:
            asset.processed_source = output
        raise EngineProcessFailed(errors)

    def get_args(self, context):
        return [self.executable] + self.params
