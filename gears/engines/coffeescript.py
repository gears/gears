import os
from .base import ExecEngine


EXECUTABLE = os.path.join(os.path.dirname(__file__), 'coffeescript.js')


class CoffeeScriptEngine(ExecEngine):

    result_mimetype = 'application/javascript'

    def __init__(self):
        super(CoffeeScriptEngine, self).__init__(EXECUTABLE)
