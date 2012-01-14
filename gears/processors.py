from __future__ import with_statement

import os
import re
import shlex

from .asset_attributes import AssetAttributes
from .assets import Asset
from .exceptions import FileNotFound


class BaseProcessor(object):

    def __init__(self, asset_attributes, source, context, calls):
        self.asset_attributes = asset_attributes
        self.environment = asset_attributes.environment
        self.path = asset_attributes.path
        self.source = source
        self.context = context
        self.calls = calls

    def process(self):
        raise NotImplementedError()


class DirectivesProcessor(BaseProcessor):

    header_re = re.compile(r'^(\s*((/\*.*?\*/)|(//[^\n]*\n?)+))+', re.DOTALL)
    directive_re = re.compile(r"""^\s*(?:\*|//|#)\s*=\s*(\w+[./'"\s\w-]*)$""")

    def __init__(self, *args, **kwargs):
        super(DirectivesProcessor, self).__init__(*args, **kwargs)
        match = self.header_re.match(self.source)
        if match:
            self.source_header = match.group(0)
            self.source_body = self.header_re.sub('', self.source)
        else:
            self.source_header = ''
            self.source_body = self.source

    def process(self):
        if not self.source_header:
            return self.source_body.strip() + '\n'
        source = self.process_directives()
        return source + '\n'

    def process_directives(self):
        preassets = []
        postassets = []
        assets = preassets
        for args in self.parse_directives(self.source_header):
            if args[0] == 'require' and len(args) == 2:
                self.process_require_directive(args[1], assets)
            elif args[0] == 'require_directory' and len(args) == 2:
                self.process_require_directory_directive(args[1], assets)
            elif args[0] == 'require_self' and len(args) == 1:
                assets = postassets
        source = [str(asset).strip() for asset in preassets]
        source.append(self.source_body.strip())
        source.extend(str(asset).strip() for asset in postassets)
        return '\n\n'.join(source).strip()

    def parse_directives(self, header):
        for line in header.splitlines():
            match = self.directive_re.match(line)
            if match:
                yield shlex.split(match.group(1))

    def process_require_directive(self, path, assets):
        try:
            asset_attributes, absolute_path = self.find(path)
        except FileNotFound:
            return
        assets.append(self.get_asset(asset_attributes, absolute_path))

    def process_require_directory_directive(self, path, assets):
        path = self.get_relative_path(path, is_directory=True)
        list = self.environment.list(path, self.asset_attributes.suffix)
        for asset_attributes, absolute_path in sorted(list, key=lambda x: x[0].path):
            assets.append(self.get_asset(asset_attributes, absolute_path))

    def find(self, require_path):
        require_path = self.get_relative_path(require_path)
        asset_attributes = AssetAttributes(self.environment, require_path)
        return self.environment.find(asset_attributes, True)

    def get_relative_path(self, require_path, is_directory=False):
        require_path = os.path.join(os.path.dirname(self.path), require_path)
        require_path = os.path.normpath(require_path)
        if is_directory:
            return require_path
        return require_path + ''.join(self.asset_attributes.extensions)

    def get_asset(self, asset_attributes, absolute_path):
        return Asset(asset_attributes, absolute_path, self.context, self.calls)
