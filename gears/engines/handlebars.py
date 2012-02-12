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

    def process(self, asset):
        asset.processed_source = super(HandlebarsEngine, self).process(asset)
        asset.processed_source = SOURCE % {
            'name': asset.get_context()['name'],
            'source': asset.processed_source}
