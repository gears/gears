from __future__ import with_statement

import os
import shlex
from functools import wraps

from .asset_attributes import AssetAttributes
from .assets import Asset
from .directives_parser import DirectivesParser


class BaseProcessor(object):

    @classmethod
    def as_processor(cls, **initkwargs):
        @wraps(cls, updated=())
        def processor(asset):
            instance = cls(**initkwargs)
            return instance.process(asset)
        return processor

    def process(self, asset):
        raise NotImplementedError()


class DirectivesProcessor(BaseProcessor):

    def __init__(self, parser=None, asset_class=None):
        self.parser = parser or DirectivesParser()
        self.asset_class = asset_class or Asset
        self.types = {
            'require': self.process_require_directive,
            'require_directory': self.process_require_directory_directive,
            'require_self': self.process_require_self_directive,
        }

    def process(self, asset):
        self.asset = asset
        self.parse()
        self.process_directives()

    def parse(self):
        directives, source = self.parser.parse(self.asset.processed_source)
        self.directives = directives
        self.asset.processed_source = source

    def process_directives(self):
        for args in (shlex.split(directive) for directive in self.directives):
            self.types[args[0]](*args[1:])

    def process_require_directive(self, path):
        self.asset.requirements.add(self.get_asset(*self.find(path)))

    def process_require_directory_directive(self, path):
        path = self.get_relative_path(path, is_directory=True)
        list = self.asset.environment.list(path, self.asset.attributes.suffix)
        for asset_attributes, absolute_path in sorted(list, key=lambda x: x[0].path):
            self.asset.requirements.add(self.get_asset(asset_attributes, absolute_path))

    def process_require_self_directive(self):
        self.asset.requirements.add(self.asset)

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
        return self.asset_class(asset_attributes, absolute_path,
                                self.asset.context, self.asset.calls)
