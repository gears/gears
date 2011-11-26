import os
from .base import ExecEngine


class LessEngine(ExecEngine):

    result_mimetype = 'text/css'
    executable = os.path.join(os.path.dirname(__file__), 'less.js')
