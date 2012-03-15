from __future__ import absolute_import

slimit_available = False
try:
    from slimit import minify
    slimit_available = True
except ImportError:
    pass

from .base import BaseCompressor
from ..exceptions import ImproperlyConfigured


class SlimItCompressor(BaseCompressor):

    def __init__(self):
        if not slimit_available:
            raise ImproperlyConfigured("Slimit is not available")

    def __call__(self, asset):
        return minify(asset.bundled_source, mangle=True)
