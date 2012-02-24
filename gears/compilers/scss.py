from .base import ExecCompiler


class SCSSCompiler(ExecCompiler):

    params = ['--stdin']
    result_mimetype = 'text/css'
