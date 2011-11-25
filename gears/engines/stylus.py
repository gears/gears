import os
from .base import ExecEngine


EXECUTABLE = os.path.join(os.path.dirname(__file__), 'stylus.js')


class StylusEngine(ExecEngine):

    result_mimetype = 'text/css'

    def __init__(self):
        super(StylusEngine, self).__init__(EXECUTABLE)
