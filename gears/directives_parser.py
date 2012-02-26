import re


class DirectivesParser(object):

    header_re = re.compile(r"""
        ^( \s* (
            ( /\* .*? \*/ ) |  # multiline comment
            ( // [^\n]* )+ |   # slash comment
            ( \# [^\n]* )+     # dash comment
        ) )+
    """, re.S | re.X)

    directive_re = re.compile(r"""
        ^ \s* (?:\*|//|\#) \s* = \s* ( \w+ [./'"\s\w-]* ) $
    """, re.X)

    def split_source(self, source):
        header_match = self.header_re.match(source)
        if not header_match:
            return '', source
        header = header_match.group(0)
        source = source[len(header):]
        return header, source

    def split_header(self, header):
        directives = []
        header_lines = []
        for line in header.splitlines():
            directive_match = self.directive_re.match(line)
            if directive_match:
                directives.append(directive_match.group(1))
            else:
                header_lines.append(line)
        return directives, '\n'.join(header_lines)

    def parse(self, source):
        header, source = self.split_source(source)
        directives, header = self.split_header(header)
        return directives, ''.join([header, source]).strip() + '\n'
