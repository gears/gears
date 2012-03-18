# -*- coding: utf-8 -*-

from ..asset_handler import BaseAssetHandler


class BaseProcessor(BaseAssetHandler):
    """Base class for all asset processors. Subclass's :meth:`__call__` method
    must change asset's :attr:`~gears.assets.Asset.processed_source` attribute.
    """
