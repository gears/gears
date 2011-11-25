from .base import ExecEngine


class SASSEngine(ExecEngine):

    params = ['--stdin']
    result_mimetype = 'text/css'
