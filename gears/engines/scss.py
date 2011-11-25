from .base import ExecEngine


class SCSSEngine(ExecEngine):

    params = ['--stdin']
    result_mimetype = 'text/css'
