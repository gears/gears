try:
    from slimit import minify
    slimit_available = True
except ImportError:
    slimit_available = False

from .base import BaseCompressor
from ..exceptions import ImproperlyConfigured


class SlimItCompressor(BaseCompressor):

    def __init__(self):
        if not slimit_available:
            raise ImproperlyConfigured('Slimit is not available')

    def __call__(self, asset):
        return minify(asset.bundled_source, mangle=True)
