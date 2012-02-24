import os
from .base import ExecCompressor


class UglifyJSCompressor(ExecCompressor):

    executable = os.path.join(os.path.dirname(__file__), 'uglifyjs.js')
