import os
from .base import ExecCompiler


class StylusCompiler(ExecCompiler):

    result_mimetype = 'text/css'
    executable = 'node'
    params = [os.path.join(os.path.dirname(__file__), 'stylus.js')]

    def __call__(self, asset):
        self.asset = asset
        super(StylusCompiler, self).__call__(asset)

    def get_args(self):
        args = super(StylusCompiler, self).get_args()
        args.append(self.asset.absolute_path)
        return args
