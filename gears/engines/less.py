import os
from .base import ExecEngine


EXECUTABLE = os.path.join(os.path.dirname(__file__), 'less.js')


class LessEngine(ExecEngine):

    result_mimetype = 'text/css'

    def __init__(self):
        super(LessEngine, self).__init__(EXECUTABLE)
