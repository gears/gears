import os
from .base import ExecEngine


EXECUTABLE = os.path.join(os.path.dirname(__file__), 'handlebars.js')

SOURCE = '\n'.join((
    "function() {",
    "  var template  = Handlebars.template,",
    "      templates = Handlebars.templates = Handlebars.templates || {};",
    "  templates['%(name)s'] = template(%(source)s);",
    "}).call(this);"))


class HandlebarsEngine(ExecEngine):

    result_mimetype = 'application/javascript'

    def __init__(self):
        super(HandlebarsEngine, self).__init__(EXECUTABLE)

    def process(self, source, context, calls):
        source = super(HandlebarsEngine, self).process(source, context, calls)
        return SOURCE % {'name': context['name'], 'source': source}
