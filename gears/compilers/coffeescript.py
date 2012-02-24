import os
from .base import ExecCompiler


class CoffeeScriptCompiler(ExecCompiler):

    result_mimetype = 'application/javascript'
    executable = 'node'
    params = [os.path.join(os.path.dirname(__file__), 'coffeescript.js')]
