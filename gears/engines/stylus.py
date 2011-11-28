import os
from .base import ExecEngine


class StylusEngine(ExecEngine):

    result_mimetype = 'text/css'
    executable = os.path.join(os.path.dirname(__file__), 'stylus.js')

    def get_args(self, context):
        return [self.executable, context['absolute_path']]
