from __future__ import with_statement

import os
import re
import shlex

from .asset_attributes import AssetAttributes
from .assets import Asset


class InvalidDirective(Exception):
    pass


class BaseProcessor(object):

    def __init__(self, asset_attributes):
        self.asset_attributes = asset_attributes
        self.environment = asset_attributes.environment
        self.path = asset_attributes.path

    def process(self, source, context, calls):
        raise NotImplementedError()


class DirectivesProcessor(BaseProcessor):

    header_re = re.compile(r'^(\s*((/\*.*?\*/)|(//[^\n]*\n?)+))+', re.DOTALL)
    directive_re = re.compile(r"""^\s*(?:\*|//)\s*=\s*(\w+[./'"\s\w-]*)$""")

    def process(self, source, context, calls):
        match = self.header_re.match(source)
        if match:
            header = match.group(0)
            body = self.header_re.sub('', source)
        else:
            header = ''
            body = source
        source = self.process_directives(header, body, context, calls)
        return '\n\n'.join(source).strip() + '\n'

    def process_directives(self, header, self_body, context, calls):
        body = []
        directive_linenos = []
        has_require_self = False
        for lineno, args in self.parse_directives(header):
            try:
                if args[0] == 'require':
                    self.process_require_directive(
                        args[1:], lineno, body, context, calls)
                elif args[0] == 'require_self':
                    self.process_require_self_directive(
                        args[1:], lineno, body, self_body)
                    has_require_self = True
                else:
                    raise InvalidDirective(
                        "%s (%s): unknown directive: %r."
                        % (self.path, lineno, args[0]))
            except InvalidDirective:
                pass
            else:
                directive_linenos.append(lineno)
        if not has_require_self:
            body.append(self_body.strip())
        header = self.strip_header(header, directive_linenos)
        return header, '\n\n'.join(body).strip()

    def strip_header(self, header, linenos):
        header = header.splitlines()
        for lineno in reversed(linenos):
            del header[lineno]
        return '\n'.join(header).strip()

    def parse_directives(self, header):
        for lineno, line in enumerate(header.splitlines()):
            match = self.directive_re.match(line)
            if match:
                yield lineno, shlex.split(match.group(1))

    def process_require_directive(self, args, lineno, body, context, calls):
        if len(args) != 1:
            raise InvalidDirective(
                "%s (%s): 'require' directive has wrong number "
                "of arguments (only one argument required): %s."
                % (self.path, lineno, args))
        asset_attributes, absolute_path = self.find(args[0])
        if not absolute_path:
            raise InvalidDirective(
                "%s (%s): required file does not exist." % (self.path, lineno))
        asset = Asset(asset_attributes, absolute_path, context, calls)
        body.append(str(asset).strip())

    def process_require_self_directive(self, args, lineno, body, self_body):
        if args:
            raise InvalidDirective(
                "%s (%s): 'require_self' directive requires no arguments."
                % self.path, lineno)
        body.append(self_body.strip())

    def find(self, require_path):
        require_path = self.get_relative_path(require_path)
        asset_attributes = AssetAttributes(self.environment, require_path)
        return self.environment.find(asset_attributes, True)

    def get_relative_path(self, require_path):
        require_path = os.path.join(os.path.dirname(self.path), require_path)
        return require_path + ''.join(self.asset_attributes.extensions)
