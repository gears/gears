import re
from .base import BaseProcessor


BLANK_RE = re.compile(r'\A\s*\Z', re.M)
SEMICOLON_RE = re.compile(r';\s*\Z', re.M)


def needs_semicolon(source):
    return (BLANK_RE.search(source) is None and
            SEMICOLON_RE.search(source) is None)


class SemicolonsProcessor(BaseProcessor):

    def __call__(self, asset):
        if needs_semicolon(asset.processed_source):
            asset.processed_source += ';\n'
