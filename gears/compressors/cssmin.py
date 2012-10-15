try:
    from cssmin import cssmin
    cssmin_available = True
except ImportError:
    cssmin_available = False

from .base import BaseCompressor
from ..exceptions import ImproperlyConfigured


class CSSMinCompressor(BaseCompressor):

    def __init__(self):
        if not cssmin_available:
            raise ImproperlyConfigured('cssmin is not available')

    def __call__(self, asset):
        return cssmin(asset.bundled_source)
