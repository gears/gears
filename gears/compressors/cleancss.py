import os
from .base import ExecCompressor


class CleanCSSCompressor(ExecCompressor):

    executable = 'node'
    params = [os.path.join(os.path.dirname(__file__), 'cleancss.js')]
