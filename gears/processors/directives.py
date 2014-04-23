import os
import shlex
import sys

from .base import BaseProcessor
from ..asset_attributes import AssetAttributes
from ..assets import Asset
from ..directives_parser import DirectivesParser
from ..exceptions import FileNotFound


class DirectivesProcessor(BaseProcessor):

    def __init__(self):
        self.types = {
            'params': self.process_params_directive,
            'require': self.process_require_directive,
            'require_directory': self.process_require_directory_directive,
            'require_tree': self.process_require_tree_directive,
            'require_self': self.process_require_self_directive,
            'depend_on': self.process_depend_on_directive,
        }

    def __call__(self, asset):
        self.asset = asset
        self.parse()
        self.process_directives()

    def parse(self):
        directives, source = DirectivesParser().parse(self.asset.processed_source)
        self.directives = directives
        self.asset.processed_source = source

    def process_directives(self):
        for directive in self.directives:
            # shlex didn't support Unicode prior to 2.7.3
            if sys.version_info < (2, 7, 3):
                directive = directive.encode('utf-8')
            args = shlex.split(directive)
            self.types[args[0]](*args[1:])

    def process_params_directive(self, *params):
        for param in params:
            if '=' in param:
                key, value = param.split('=', 1)
                self.asset.params[key] = value

    def process_require_directive(self, path):
        found = False
        path = self.get_relative_path(path)
        list = self.asset.attributes.environment.list(path, self.asset.attributes.mimetype)
        for asset_attributes, absolute_path in sorted(list, key=lambda x: x[0].path.split('/')):
            self.asset.requirements.add(self.get_asset(asset_attributes, absolute_path))
            self.asset.dependencies.add(os.path.dirname(absolute_path))
            found = True
        if not found:
            raise FileNotFound(path)

    def process_require_directory_directive(self, path):
        self.process_require_directive(os.path.join(path, '*'))

    def process_require_tree_directive(self, path):
        self.process_require_directive(os.path.join(path, '**'))

    def process_require_self_directive(self):
        self.asset.requirements.add(self.asset)

    def process_depend_on_directive(self, path):
        found = False
        path = self.get_relative_path(path)
        list = self.asset.attributes.environment.list(path, self.asset.attributes.mimetype)
        for asset_attributes, absolute_path in list:
            self.asset.dependencies.add(absolute_path)
            found = True
        if not found:
            raise FileNotFound(path)

    def get_relative_path(self, require_path, is_directory=False):
        require_path = os.path.join(self.asset.attributes.dirname, require_path)
        return os.path.normpath(require_path)

    def get_asset(self, asset_attributes, absolute_path):
        return Asset(asset_attributes, absolute_path, self.asset.calls)
