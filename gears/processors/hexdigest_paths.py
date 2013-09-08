import os
import re
from ..assets import build_asset
from ..exceptions import FileNotFound
from .base import BaseProcessor


URL_RE = re.compile(r"""url\((['"]?)\s*(.*?)\s*\1\)""")


def rewrite_paths(source, func):
    repl = lambda match: 'url({quote}{path}{quote})'.format(
        quote=match.group(1),
        path=func(match.group(2)),
    )
    return URL_RE.sub(repl, source)


class HexdigestPathsProcessor(BaseProcessor):

    url_re = re.compile(r"""url\((['"]?)\s*(.*?)\s*\1\)""")

    def __call__(self, asset):
        self.asset = asset
        self.environment = self.asset.attributes.environment
        self.current_dir = self.asset.attributes.dirname
        self.process()

    def process(self):
        if self.environment.fingerprinting:
            self.asset.processed_source = rewrite_paths(
                self.asset.processed_source,
                self.rewrite_path,
            )

    def rewrite_path(self, path):
        logical_path = os.path.normpath(os.path.join(self.current_dir, path))
        try:
            asset = build_asset(self.environment, logical_path)
        except FileNotFound:
            return path
        self.asset.dependencies.add(asset.absolute_path)
        return os.path.relpath(asset.hexdigest_path, self.current_dir)
