import os
import shlex
import sys

from .base import BaseProcessor
from ..asset_attributes import AssetAttributes
from ..assets import Asset
from ..directives_parser import DirectivesParser


class DirectivesProcessor(BaseProcessor):

    def __init__(self):
        self.types = {
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

    def process_require_directive(self, path):
        self.asset.requirements.add(self.get_asset(*self.find(path)))

    def process_require_directory_directive(self, path, recursive=False):
        path = self.get_relative_path(path, is_directory=True)
        list = self.asset.attributes.environment.list(path, self.asset.attributes.mimetype, recursive=recursive)
        for asset_attributes, absolute_path in sorted(list, key=lambda x: x[0].path.split('/')):
            self.asset.requirements.add(self.get_asset(asset_attributes, absolute_path))
            self.asset.dependencies.add(os.path.dirname(absolute_path))

    def process_require_tree_directive(self, path):
        self.process_require_directory_directive(path, recursive=True)

    def process_require_self_directive(self):
        self.asset.requirements.add(self.asset)

    def process_depend_on_directive(self, path):
        self.asset.dependencies.add(self.find(path)[1])

    def find(self, require_path):
        require_path = self.get_relative_path(require_path)
        asset_attributes = AssetAttributes(self.asset.attributes.environment, require_path)
        return self.asset.attributes.environment.find(asset_attributes, True)

    def get_relative_path(self, require_path, is_directory=False):
        require_path = os.path.join(self.asset.attributes.dirname, require_path)
        require_path = os.path.normpath(require_path)
        if is_directory:
            return require_path
        return require_path + ''.join(self.asset.attributes.extensions)

    def get_asset(self, asset_attributes, absolute_path):
        return Asset(asset_attributes, absolute_path, self.asset.calls)
