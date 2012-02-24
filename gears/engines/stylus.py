import os
from .base import ExecEngine


class StylusEngine(ExecEngine):

    result_mimetype = 'text/css'
    executable = 'node'
    params = [os.path.join(os.path.dirname(__file__), 'stylus.js')]

    def get_args(self):
        args = super(StylusEngine, self).get_args()
        args.append(self.asset.absolute_path)
        return args
