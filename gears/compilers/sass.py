from .base import ExecCompiler


class SASSCompiler(ExecCompiler):

    params = ['--stdin']
    result_mimetype = 'text/css'
