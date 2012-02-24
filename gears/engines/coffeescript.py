import os
from .base import ExecEngine


class CoffeeScriptEngine(ExecEngine):

    result_mimetype = 'application/javascript'
    executable = 'node'
    params = [os.path.join(os.path.dirname(__file__), 'coffeescript.js')]
