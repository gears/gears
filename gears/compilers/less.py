import os
from .base import ExecCompiler


class LessCompiler(ExecCompiler):

    result_mimetype = 'text/css'
    executable = 'node'
    params = [os.path.join(os.path.dirname(__file__), 'less.js')]
