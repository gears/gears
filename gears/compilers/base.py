# -*- coding: utf-8 -*-

from ..asset_handler import BaseAssetHandler, ExecMixin


class BaseCompiler(BaseAssetHandler):
    """Base class for all asset compilers. Subclass's :meth:`__call__` method
    must change asset's :attr:`~gears.assets.Asset.processed_source` attribute.
    """

    #: MIME type of the asset source code after compiling.
    result_mimetype = None

    @classmethod
    def as_handler(cls, **initkwargs):
        handler = super(BaseCompiler, cls).as_handler(**initkwargs)
        handler.result_mimetype = cls.result_mimetype
        return handler


class ExecCompiler(BaseCompiler, ExecMixin):

    def __init__(self, executable=None):
        if executable is not None:
            self.executable = executable

    def __call__(self, asset):
        asset.processed_source = self.run(asset.processed_source)
