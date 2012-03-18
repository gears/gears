# -*- coding: utf-8 -*-

from ..asset_handler import BaseAssetHandler, ExecMixin


class BaseCompressor(BaseAssetHandler):
    """Base class for all asset compressors. Subclass's :meth:`__call__` method
    must return compressed :attr:`~gears.assets.Asset.bundled_source` attribute.
    """


class ExecCompressor(BaseCompressor, ExecMixin):

    def __init__(self, executable=None):
        if executable is not None:
            self.executable = executable

    def __call__(self, asset):
        return self.run(asset.bundled_source)
