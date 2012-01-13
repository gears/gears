import os
from .base import ExecEngine


SOURCE = '\n'.join((
    "(function() {",
    "  var template  = Handlebars.template,",
    "      templates = Handlebars.templates = Handlebars.templates || {};",
    "  templates['%(name)s'] = template(%(source)s);",
    "}).call(this);"))


class HandlebarsEngine(ExecEngine):

    result_mimetype = 'application/javascript'
    executable = os.path.join(os.path.dirname(__file__), 'handlebars.js')

    def process(self, source, context):
        source = super(HandlebarsEngine, self).process(source, context)
        return SOURCE % {'name': context['name'], 'source': source}
